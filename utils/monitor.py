import psutil
import time
import pygetwindow as gw
from datetime import datetime
import os
import csv
import json
import win32process

from utils.logger import save_to_csv, save_to_json

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            info = proc.info
            processes.append({
                'pid': info['pid'],
                'name': info['name'],
                'cpu_percent': info['cpu_percent'],
                'memory': info['memory_info'].rss / (1024 * 1024)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def get_process_name_from_window(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except Exception:
        return "Unknown"

def format_duration(seconds):
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds} sec"
    else:
        minutes = seconds // 60
        remaining = seconds % 60
        return f"{minutes} min {remaining} sec" if remaining else f"{minutes} min"

def track_active_window_time(duration=0, interval=2):
    start_time = time.time()
    app_times = {}
    last_active = None
    last_switch_time = time.time()

    try:
        while duration == 0 or (time.time() - start_time) < duration:
            try:
                active_window = gw.getActiveWindow()
                if active_window is not None:
                    app_title = active_window.title
                else:
                    app_title = "No active window"

                if app_title != last_active:
                    if last_active:
                        time_spent = time.time() - last_switch_time
                        app_times[last_active] = app_times.get(last_active, 0) + time_spent
                        print(f" {last_active} : +{time_spent:.2f} sec")
                    last_active = app_title
                    last_switch_time = time.time()

                time.sleep(interval)

            except Exception as e:
                print(f"Error : {e}")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\n Interrupted by user. Saving log...")

    if last_active:
        time_spent = time.time() - last_switch_time
        app_times[last_active] = app_times.get(last_active, 0) + time_spent
        print(f" {last_active} : +{time_spent:.2f} sec")

    now = datetime.now()
    log_data = []
    for app_name, duration in app_times.items():
        log_data.append({
            "app_name": app_name,
            "duration_seconds": duration,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S")
        })

    save_to_csv(log_data)
    save_to_json(log_data)

    return app_times

def start_monitoring():
    track_active_window_time(duration=0, interval=2)

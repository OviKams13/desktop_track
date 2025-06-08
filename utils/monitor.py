import psutil
import time
import pygetwindow as gw
from datetime import datetime
import os
import csv
import json
import win32process
import sys
import threading

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

    def auto_save_loop():
        while True:
            time.sleep(120)  # Save every 2 minutes
            if app_times:
                now = datetime.now()
                log_data = []
                for app_name, duration_secs in app_times.items():
                    log_data.append({
                        "app_name": app_name,
                        "duration_seconds": duration_secs,
                        "date": now.strftime("%Y-%m-%d"),
                        "time": now.strftime("%H:%M:%S")
                    })
                save_to_csv(log_data)
                save_to_json(log_data)
                app_times.clear()

    threading.Thread(target=auto_save_loop, daemon=True).start()

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

def add_to_startup():
    try:
        import win32com.client
        startup_path = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shortcut_path = os.path.join(startup_path, "DesktopTracker.lnk")
        if getattr(sys, 'frozen', False):
            # If running as compiled .exe
            target = sys.executable
        else:
            # If running as script
            target = os.path.abspath(__file__)

        if not os.path.exists(shortcut_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.save()
            print(" App added to Windows startup.")
        else:
            print(" App is already set to launch at startup.")
    except Exception as e:
        print(f" Failed to add to startup: {e}")

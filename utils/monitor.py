import psutil
import time
import pygetwindow as gw
from datetime import datetime
import os
import csv
import json
import win32process
import subprocess
import threading

TARGET_GIT_REPO = r"C:\Users\okamb\OneDrive\Desktop\Project"

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
                    app_title = "Aucune fenêtre active"

                if app_title != last_active:
                    if last_active:
                        time_spent = time.time() - last_switch_time
                        app_times[last_active] = app_times.get(last_active, 0) + time_spent
                        print(f"⏱️ {last_active} : +{time_spent:.2f} sec")
                    last_active = app_title
                    last_switch_time = time.time()

                time.sleep(interval)

            except Exception as e:
                print(f"Erreur : {e}")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\n🛑 Interrompu par l'utilisateur. Sauvegarde du log...")

    if last_active:
        time_spent = time.time() - last_switch_time
        app_times[last_active] = app_times.get(last_active, 0) + time_spent
        print(f"⏱️ {last_active} : +{time_spent:.2f} sec")

    save_log(app_times, "data/activity_log")
    return app_times

def track_git_activity(interval=10):
    last_commit = None
    while True:
        try:
            result = subprocess.run(["git", "-C", TARGET_GIT_REPO, "log", "-1", "--pretty=format:%H|%s|%ci"],
                                    capture_output=True, text=True)
            output = result.stdout.strip()
            if output:
                commit_hash, commit_msg, commit_date = output.split("|")
                if commit_hash != last_commit:
                    last_commit = commit_hash
                    print(f"📢 Nouveau commit détecté : {commit_msg} ({commit_date})")
                    save_log({f"Commit: {commit_msg}": 0}, "data/git_activity_log", commit_date)
            time.sleep(interval)
        except Exception as e:
            print(f"Git monitoring error: {e}")
            time.sleep(interval)

def save_log(data_dict, filename_base, timestamp=None):
    os.makedirs(os.path.dirname(f"{filename_base}.csv"), exist_ok=True)
    date_str = timestamp.split()[0] if timestamp else datetime.now().strftime("%Y-%m-%d")
    time_str = timestamp.split()[1] if timestamp else datetime.now().strftime("%H:%M:%S")
    with open(f"{filename_base}.csv", mode='a', newline='', encoding='utf-8-sig') as f:

        writer = csv.writer(f)
        if os.stat(f"{filename_base}.csv").st_size == 0:
            writer.writerow(["event", "duration", "date", "time"])
        for key in data_dict:
            writer.writerow([key, format_duration(data_dict[key]), date_str, time_str])
    if os.path.exists(f"{filename_base}.json"):
        with open(f"{filename_base}.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    for key in data_dict:
        existing_data.append({"event": key, "duration": format_duration(data_dict[key]), "date": date_str, "time": time_str})
    with open(f"{filename_base}.json", "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)

def start_monitoring():
    git_thread = threading.Thread(target=track_git_activity, daemon=True)
    git_thread.start()
    track_active_window_time(duration=0, interval=2)  # Run forever until Ctrl + C

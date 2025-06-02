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

# Set this to the path of your target repository
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

def normalize_app_name(app_title, process_name):
    title = app_title.lower()
    process = process_name.lower()
    if "x" in title or "twitter" in title:
        base = "X"
    elif "youtube" in title:
        base = "YouTube"
    elif "whatsapp" in title:
        base = "WhatsApp"
    elif "spotify" in title:
        base = "Spotify"
    elif "facebook" in title:
        base = "Facebook"
    elif "instagram" in title:
        base = "Instagram"
    elif "snapchat" in title:
        base = "Snapchat"
    elif "tiktok" in title:
        base = "TikTok"
    elif "netflix" in title:
        base = "Netflix"
    elif "teams" in title:
        base = "Microsoft Teams"
    elif "slack" in title:
        base = "Slack"
    elif "google docs" in title:
        base = "Google Docs"
    elif "meet" in title:
        base = "Google Meet"
    elif "zoom" in title:
        base = "Zoom"
    elif "linkedin" in title:
        base = "LinkedIn"
    elif "excel" in title:
        base = "Microsoft Excel"
    elif "word" in title:
        base = "Microsoft Word"
    elif "visual studio code" in title or "vscode" in title:
        base = "Visual Studio Code"
    elif "chrome" in process:
        base = "Google Chrome"
    elif "firefox" in process:
        base = "Mozilla Firefox"
    elif "edge" in process:
        base = "Microsoft Edge"
    else:
        return app_title
    if "chrome" in process or "firefox" in process or "edge" in process:
        return f"{base} - {process_name}"
    else:
        return base

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
                    hwnd = active_window._hWnd
                    app_title = active_window.title
                    process_name = get_process_name_from_window(hwnd)
                    normalized_name = normalize_app_name(app_title, process_name)
                else:
                    normalized_name = "No Active Window"

                if normalized_name != last_active:
                    if last_active:
                        time_spent = time.time() - last_switch_time
                        app_times[last_active] = app_times.get(last_active, 0) + time_spent
                        print(f"⏱️ {last_active} : +{time_spent:.2f} sec")
                    last_active = normalized_name
                    last_switch_time = time.time()

                time.sleep(interval)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted by user. Saving log...")

    if last_active:
        time_spent = time.time() - last_switch_time
        app_times[last_active] = app_times.get(last_active, 0) + time_spent

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
                    print(f"📢 New commit detected in {TARGET_GIT_REPO}: {commit_msg} at {commit_date}")
                    save_log({f"Commit: {commit_msg}": 0}, "data/git_activity_log", commit_date)
            time.sleep(interval)
        except Exception as e:
            print(f"Git monitoring error: {e}")
            time.sleep(interval)

def save_log(data_dict, filename_base, timestamp=None):
    os.makedirs(os.path.dirname(f"{filename_base}.csv"), exist_ok=True)
    date_str = timestamp.split()[0] if timestamp else datetime.now().strftime("%Y-%m-%d")
    time_str = timestamp.split()[1] if timestamp else datetime.now().strftime("%H:%M:%S")
    with open(f"{filename_base}.csv", mode='a', newline='', encoding='utf-8') as f:
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
    track_active_window_time()

if __name__ == "__main__":
    start_monitoring()

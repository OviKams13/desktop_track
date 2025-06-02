from utils.monitor import get_running_processes, monitor_processes
from utils.monitor import monitor_active_window, monitor_specific_apps
from utils.logger import save_to_csv, save_to_json
from utils.monitor import track_active_window_time
from datetime import datetime  # ADDED to use datetime for logging

if __name__ == "__main__":
    processes = get_running_processes()  # KEPT the function call but REMOVED print output

    print("\n🎯 Mesure du temps d'activité par application (3 minutes) :")
    activity_times = track_active_window_time(duration=180, interval=2)  # CHANGED duration from 60 to 180

    # Prepare data for logging (ADDED logging for tracked data)
    log_entry = []
    for app_name, total_time in activity_times.items():
        log_entry.append({
            "app_name": app_name,
            "duration_seconds": round(total_time, 2),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S")
        })

    save_to_csv(log_entry)
    save_to_json(log_entry)

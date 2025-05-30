from utils.monitor import get_running_processes, monitor_processes
from utils.monitor import monitor_active_window, monitor_specific_apps
from utils.logger import save_to_csv, save_to_json
from utils.monitor import track_active_window_time

if __name__ == "__main__":
    print("📋 Liste des processus en cours :")
    processes = get_running_processes()
    for p in processes:
        print(f"PID: {p['pid']}, Nom: {p['name']}, CPU: {p['cpu_percent']}%, Mémoire: {p['memory']:.2f} Mo")

    print("\n⏱️ Surveillance des processus (30 secondes) :")
    times = monitor_processes(duration=30, interval=5)
    for pid, info in times.items():
        print(f"PID: {pid}, Nom: {info['name']}, Temps CPU cumulé: {info['cpu_time']:.2f} sec")

if __name__ == "__main__":
    print("\n📋 Suivi des fenêtres actives (30 secondes) :")
    monitor_active_window(duration=30, interval=5)

    print("\n🎯 Détection spécifique (YouTube ou Word) :")
    monitor_specific_apps(duration=30, interval=5)

if __name__ == "__main__":
    log_entry = [
        {"app_name": "YouTube - Chrome", "duration_seconds": 120, "date": "2025-05-30", "time": "15:20:10"},
        {"app_name": "Microsoft Word", "duration_seconds": 300, "date": "2025-05-30", "time": "15:25:40"}
    ]

    save_to_csv(log_entry)
    save_to_json(log_entry)

if __name__ == "__main__":
    print("\n🎯 Mesure du temps d'activité par application :")
    activity_times = track_active_window_time(duration=60, interval=2)
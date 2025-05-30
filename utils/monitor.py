import psutil
import time
import pygetwindow as gw
from datetime import datetime

def get_running_processes():
    """
    Récupère la liste des processus en cours avec leurs détails.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            info = proc.info
            processes.append({
                'pid': info['pid'],
                'name': info['name'],
                'cpu_percent': info['cpu_percent'],
                'memory': info['memory_info'].rss / (1024 * 1024)  # Convertir en Mo
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

import time

def monitor_processes(duration=60, interval=5):
    """
    Surveille les processus pendant 'duration' secondes,
    avec un intervalle entre les vérifications.
    """
    start_time = time.time()
    process_times = {}

    while (time.time() - start_time) < duration:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                times = proc.cpu_times()
                cpu_time = times.user + times.system

                if pid not in process_times:
                    process_times[pid] = {'name': name, 'cpu_time': cpu_time, 'start_time': time.time()}
                else:
                    process_times[pid]['cpu_time'] = cpu_time

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(interval)

    return process_times

def get_active_window_title():
    """
    Récupère le titre de la fenêtre active.
    """
    try:
        active_window = gw.getActiveWindow()
        if active_window is not None:
            return active_window.title
        else:
            return "Aucune fenêtre active"
    except Exception as e:
        return f"Erreur : {e}"
    
def monitor_active_window(duration=60, interval=5):
    """
    Surveille la fenêtre active pendant 'duration' secondes,
    avec vérification toutes les 'interval' secondes.
    """
    start_time = time.time()
    previous_title = None

    while (time.time() - start_time) < duration:
        current_title = get_active_window_title()
        if current_title != previous_title:
            print(f"Changement de fenêtre : {current_title}")
            previous_title = current_title
        time.sleep(interval)

def monitor_specific_apps(duration=60, interval=5):
    """
    Surveille si l'utilisateur est sur YouTube (Chrome) ou Microsoft Word.
    """
    start_time = time.time()

    while (time.time() - start_time) < duration:
        current_title = get_active_window_title().lower()
        if "chrome" in current_title and "youtube" in current_title:
            print("🎥 L'utilisateur est sur YouTube")
        elif "word" in current_title:
            print("📝 L'utilisateur est sur Microsoft Word")
        time.sleep(interval)

def track_active_window_time(duration=60, interval=2):
    """
    Mesure combien de temps chaque application reste active.
    duration : durée totale de la surveillance (en secondes)
    interval : temps entre chaque vérification (en secondes)
    """
    start_time = time.time()
    app_times = {}  # Stocke le temps total par application
    last_active = None
    last_switch_time = time.time()

    while (time.time() - start_time) < duration:
        try:
            active_window = gw.getActiveWindow()
            if active_window is not None:
                app_name = active_window.title
            else:
                app_name = "Aucune fenêtre"

            # Si l'application a changé
            if app_name != last_active:
                if last_active:
                    # Calculer le temps passé sur l'application précédente
                    time_spent = time.time() - last_switch_time
                    app_times[last_active] = app_times.get(last_active, 0) + time_spent
                    print(f"⏱️ {last_active} : +{time_spent:.2f} sec")
                # Mise à jour
                last_active = app_name
                last_switch_time = time.time()

            time.sleep(interval)

        except Exception as e:
            print(f"Erreur : {e}")
            time.sleep(interval)

    # Enregistrer le temps pour la dernière application
    if last_active:
        time_spent = time.time() - last_switch_time
        app_times[last_active] = app_times.get(last_active, 0) + time_spent
        print(f"⏱️ {last_active} : +{time_spent:.2f} sec")

    # Résultats finaux
    print("\n📋 Temps total par application :")
    for app, total_time in app_times.items():
        print(f"{app} : {total_time:.2f} sec")
    return app_times
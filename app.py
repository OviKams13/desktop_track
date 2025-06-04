from utils.monitor import get_running_processes, start_monitoring

if __name__ == "__main__":
    processes = get_running_processes()
    print("\n🎯 Mesure du temps d'activité par application (infinie)...")
    start_monitoring()

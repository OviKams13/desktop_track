from utils.monitor import get_running_processes, start_monitoring

if __name__ == "__main__":
    processes = get_running_processes()
    print("\n Measuring application activity time (infinite)...")
    start_monitoring()

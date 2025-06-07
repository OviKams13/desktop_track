from utils.monitor import get_running_processes, start_monitoring, add_to_startup

if __name__ == "__main__":
    add_to_startup()
    processes = get_running_processes()
    print("\n Measuring application activity time (infinite)...")
    start_monitoring()

from utils.monitor import get_running_processes, start_monitoring
from datetime import datetime

if __name__ == "__main__":
    processes = get_running_processes()  # This gets the running processes, but doesn't print them
    print("\n🎯 Starting monitoring (windows + git)...")
    start_monitoring()

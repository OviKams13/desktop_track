import csv
import json
from datetime import datetime
import os
import threading
import time

def format_duration(seconds):
    seconds = int(round(seconds))
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    else:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''} and {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"

def write_buffer(buffer_data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if filename.endswith('.csv'):
        fieldnames = ["app_name", "duration", "date", "time"]
        with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if os.stat(filename).st_size == 0:
                writer.writeheader()
            for row in buffer_data:
                writer.writerow(row)
    elif filename.endswith('.json'):
        if os.path.exists(filename):
            with open(filename, mode='r', encoding='utf-8') as file:
                existing_data = json.load(file)
        else:
            existing_data = []
        existing_data.extend(buffer_data)
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4)

def try_merge_buffer():
    while True:
        try:
            if os.path.exists("data/buffer_log.csv"):
                with open("data/buffer_log.csv", newline='', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)
                os.remove("data/buffer_log.csv")
                write_buffer(rows, "data/activity_log.csv")
                print(" Buffered CSV merged.")
            if os.path.exists("data/buffer_log.json"):
                with open("data/buffer_log.json", encoding='utf-8') as file:
                    rows = json.load(file)
                os.remove("data/buffer_log.json")
                write_buffer(rows, "data/activity_log.json")
                print(" Buffered JSON merged.")
        except Exception as e:
            print(f" Buffer merge error: {e}")
        time.sleep(60)

# Start background thread
threading.Thread(target=try_merge_buffer, daemon=True).start()

def save_to_csv(data, filename="data/activity_log.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fieldnames = ["app_name", "duration", "date", "time"]
    file_exists = os.path.exists(filename)
    try:
        with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in data:
                writer.writerow({
                    "app_name": row["app_name"],
                    "duration": format_duration(row["duration_seconds"]),
                    "date": row["date"],
                    "time": row["time"]
                })
        print(f" Data added to {filename}")
    except PermissionError:
        print(f" CSV is locked. Saving to buffer...")
        buffer_data = [{
            "app_name": row["app_name"],
            "duration": format_duration(row["duration_seconds"]),
            "date": row["date"],
            "time": row["time"]
        } for row in data]
        write_buffer(buffer_data, "data/buffer_log.csv")

def save_to_json(data, filename="data/activity_log.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        if os.path.exists(filename):
            with open(filename, mode='r', encoding='utf-8') as file:
                existing_data = json.load(file)
        else:
            existing_data = []
        existing_data.extend(data)
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4)
        print(f" Data added to {filename}")
    except PermissionError:
        print(f" JSON is locked. Saving to buffer...")
        write_buffer(data, "data/buffer_log.json")

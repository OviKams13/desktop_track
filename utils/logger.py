import csv
import json
from datetime import datetime
import os

def format_duration(seconds):
    """
    Converts a number of seconds into a human-readable string.
    """
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

def save_to_csv(data, filename="data/activity_log.csv"):
    """
    Saves a list of dictionaries to a CSV file by appending new entries.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fieldnames = ["app_name", "duration", "date", "time"]  # Updated header
    file_exists = os.path.exists(filename)
    try:
        with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in data:
                writer.writerow({
                    "app_name": row["app_name"],
                    "duration": format_duration(row["duration_seconds"]),  # Use formatted duration
                    "date": row["date"],
                    "time": row["time"]
                })
        print(f" Data added to {filename}")
    except PermissionError:
        print(f" Error: The file {filename} is already open. Please close it and try again.")

def save_to_json(data, filename="data/activity_log.json"):
    """
    Saves a list of dictionaries to a JSON file by appending new entries.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        # Charger les anciennes données si le fichier existe
        if os.path.exists(filename):
            with open(filename, mode='r', encoding='utf-8') as file:
                existing_data = json.load(file)
        else:
            existing_data = []
        # Ajouter les nouvelles entrées
        existing_data.extend(data)
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4)
        print(f" Data added to {filename}")
    except PermissionError:
        print(f" Error: The file {filename} is already open. Please close it and try again.")

import csv
import json
from datetime import datetime

def save_to_csv(data, filename="data/activity_log.csv"):
    """
    Enregistre une liste de dictionnaires dans un fichier CSV.
    """
    fieldnames = data[0].keys() if data else []
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"✅ Données sauvegardées dans {filename}")

def save_to_json(data, filename="data/activity_log.json"):
    """
    Enregistre une liste de dictionnaires dans un fichier JSON.
    """
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"✅ Données sauvegardées dans {filename}")

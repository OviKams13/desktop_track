import csv
import json
from datetime import datetime
import os  # Ajout pour créer le dossier si nécessaire

def save_to_csv(data, filename="data/activity_log.csv"):
    """
    Enregistre une liste de dictionnaires dans un fichier CSV.
    """
    # Crée le dossier s'il n'existe pas
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fieldnames = data[0].keys() if data else []
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        print(f"✅ Données sauvegardées dans {filename}")
    except PermissionError:
        print(f"❌ Erreur : Le fichier {filename} est déjà ouvert dans une autre application. Veuillez le fermer et réessayer.")

def save_to_json(data, filename="data/activity_log.json"):
    """
    Enregistre une liste de dictionnaires dans un fichier JSON.
    """
    # Crée le dossier s'il n'existe pas
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"✅ Données sauvegardées dans {filename}")
    except PermissionError:
        print(f"❌ Erreur : Le fichier {filename} est déjà ouvert dans une autre application. Veuillez le fermer et réessayer.")

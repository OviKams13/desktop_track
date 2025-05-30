import tkinter as tk
from tkinter import ttk
from utils.monitor import track_active_window_time

def start_monitoring():
    duration = 30  # Durée en secondes
    interval = 2
    result = track_active_window_time(duration, interval)
    output_text.delete(1.0, tk.END)
    for app, total_time in result.items():
        output_text.insert(tk.END, f"{app} : {total_time:.2f} sec\n")

# Création de la fenêtre principale
root = tk.Tk()
root.title("Moniteur d'Activité")

# Bouton de démarrage
start_button = ttk.Button(root, text="Démarrer le suivi", command=start_monitoring)
start_button.pack(pady=10)

# Zone de texte pour les résultats
output_text = tk.Text(root, height=15, width=50)
output_text.pack(pady=10)

# Boucle principale
root.mainloop()

import time
import threading
from SimConnect import *
import tkinter as tk
import math
import json
import os
from tkinter import simpledialog, messagebox


# === COULEURS PERSONNALISABLES ===
COLORS = {
    "bg": "#f4f4f4",
    "circle": "#000000",
    "circle_line": "#aaa",
    "diag_line": "#ccc",
    "graduation": "#666",
    "label_text": "#555",
    "horizontal_point": "red",
    "altitude_point": "red",
    "altitude_marker": "blue",
    "aligned": "green",
}



# === CONFIGURATION ===
DEFAULT_SETTINGS = {
    "activation_key": "f",
    "circles_meters": [2, 5, 10],
    "altitude_range": 40,
    "alignment_tolerance": {
        "horizontal_m": 1.0,
        "vertical_ft": 1.0
    }
}

SETTINGS_FILE = "settings.json"


def ouvrir_parametres():
    top = tk.Toplevel(root)
    top.title("Paramètres HSV")
    top.geometry("300x300")

    tk.Label(top, text="Touche activation HSV").pack()
    entry_key = tk.Entry(top)
    entry_key.insert(0, activation_key)
    entry_key.pack()

    tk.Label(top, text="Cercles (en mètres, séparés par des virgules)").pack()
    entry_circles = tk.Entry(top)
    entry_circles.insert(0, ", ".join(map(str, circles_meters)))
    entry_circles.pack()

    tk.Label(top, text="Échelle altitude (±x ft)").pack()
    entry_alt = tk.Entry(top)
    entry_alt.insert(0, str(altitude_range))
    entry_alt.pack()

    tk.Label(top, text="Tolérance position (m)").pack()
    entry_tol_pos = tk.Entry(top)
    entry_tol_pos.insert(0, str(tolerance_horizontal))
    entry_tol_pos.pack()

    tk.Label(top, text="Tolérance altitude (ft)").pack()
    entry_tol_alt = tk.Entry(top)
    entry_tol_alt.insert(0, str(tolerance_vertical))
    entry_tol_alt.pack()

    def sauvegarder():
        try:
            new_key = entry_key.get().strip().lower()
            new_circles = list(map(float, entry_circles.get().split(",")))
            new_alt_range = int(entry_alt.get())
            new_tol_pos = float(entry_tol_pos.get())
            new_tol_alt = float(entry_tol_alt.get())

            new_settings = {
                "activation_key": new_key,
                "circles_meters": new_circles,
                "altitude_range": new_alt_range,
                "alignment_tolerance": {
                    "horizontal_m": new_tol_pos,
                    "vertical_ft": new_tol_alt
                }
            }

            with open(SETTINGS_FILE, "w") as f:
                json.dump(new_settings, f, indent=4)

            messagebox.showinfo("Succès", "Paramètres sauvegardés ! Redémarrage des variables.")

            # Recharger les valeurs globales
            global activation_key, circles_meters, altitude_range, tolerance_horizontal, tolerance_vertical
            activation_key = new_key
            circles_meters = new_circles
            altitude_range = new_alt_range
            tolerance_horizontal = new_tol_pos
            tolerance_vertical = new_tol_alt

            top.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

    tk.Button(top, text="Sauvegarder", command=sauvegarder).pack(pady=10)


# Crée ou charge le fichier settings.json
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)
        print("✅ Fichier settings.json créé avec les valeurs par défaut.")

with open(SETTINGS_FILE, "r") as f:
    SETTINGS = json.load(f)

# === Variables issues du fichier ===
activation_key = SETTINGS.get("activation_key", "f").lower()
circles_meters = SETTINGS.get("circles_meters", [2, 5, 10])
altitude_range = SETTINGS.get("altitude_range", 40)
tolerance_horizontal = SETTINGS["alignment_tolerance"]["horizontal_m"]
tolerance_vertical = SETTINGS["alignment_tolerance"]["vertical_ft"]


# Connexion à MSFS
sm = SimConnect()
aq = AircraftRequests(sm, _time=200)

reference_data = {
    "lat": None,
    "lon": None,
    "alt": None,
    "active": False
}

# Fenêtre principale
root = tk.Tk()
root.title("HSV - Helicopter Stabilisation Visualisator")
root.geometry("500x420")
root.resizable(False, False)

canvas = tk.Canvas(root, width=500, height=400, bg="#f4f4f4")
canvas.pack()
drawn_graduations = []
drawn_labels = []

def draw_reference_elements():
    # Supprimer anciens éléments
    for el in drawn_graduations + drawn_labels:
        canvas.delete(el)
    drawn_graduations.clear()
    drawn_labels.clear()

    # Cercles
    for m in circles_meters:
        scale = m / max(circles_meters)
        circle = canvas.create_oval(
            circle_center[0] - circle_radius * scale,
            circle_center[1] - circle_radius * scale,
            circle_center[0] + circle_radius * scale,
            circle_center[1] + circle_radius * scale,
            outline="#bbb", dash=(2, 2)
        )
        label = canvas.create_text(circle_center[0] + circle_radius * scale + 10, circle_center[1],
                                   text=f"{m}m", font=("Arial", 8), fill="#555")
        drawn_graduations.append(circle)
        drawn_labels.append(label)

    # Altitude graduations
    graduation_step = altitude_range // 2
    for i in range(-2, 3):
        val = i * graduation_step
        y = (bar_top + bar_bottom) / 2 - (val / altitude_range) * 100
        line = canvas.create_line(bar_x - 10, y, bar_x + 10, y, fill="#666")
        text = canvas.create_text(bar_x + 25, y, text=f"{val:+} ft", font=("Arial", 9))
        drawn_graduations.append(line)
        drawn_labels.append(text)


# Coordonnées UI
circle_center = (150, 200)
circle_radius = 100
bar_top = 100
bar_bottom = 300
bar_x = 400

# Cercle
canvas.create_oval(
    circle_center[0] - circle_radius,
    circle_center[1] - circle_radius,
    circle_center[0] + circle_radius,
    circle_center[1] + circle_radius,
    outline="black", width=2
)

# Repères dans le cercle
canvas.create_line(circle_center[0] - circle_radius, circle_center[1], circle_center[0] + circle_radius, circle_center[1], fill="#aaa", dash=(4, 2))
canvas.create_line(circle_center[0], circle_center[1] - circle_radius, circle_center[0], circle_center[1] + circle_radius, fill="#aaa", dash=(4, 2))
canvas.create_line(circle_center[0] - circle_radius * 0.7, circle_center[1] - circle_radius * 0.7, circle_center[0] + circle_radius * 0.7, circle_center[1] + circle_radius * 0.7, fill="#ccc", dash=(3, 2))
canvas.create_line(circle_center[0] - circle_radius * 0.7, circle_center[1] + circle_radius * 0.7, circle_center[0] + circle_radius * 0.7, circle_center[1] - circle_radius * 0.7, fill="#ccc", dash=(3, 2))

# Barre verticale
canvas.create_line(bar_x, bar_top, bar_x, bar_bottom, fill="black", width=3)

# Cercles de repères (2m, 5m, 10m)


# Points visuels
horiz_point = canvas.create_oval(0, 0, 0, 0, fill="red")
alt_point = canvas.create_oval(0, 0, 0, 0, fill="red")
alt_ref_marker = canvas.create_oval(bar_x - 6, 195 - 6, bar_x + 6, 195 + 6, fill="blue")

# Lissage positions
last_x, last_y = circle_center
last_alt_y = (bar_top + bar_bottom) / 2


# Activer le HSV (référence)
def activer_hsv():
    try:
        lat = aq.get("PLANE_LATITUDE")
        lon = aq.get("PLANE_LONGITUDE")
        alt = aq.get("PLANE_ALTITUDE")

        if None in (lat, lon, alt):
            print("Impossible d'activer HSV : données manquantes.")
            return

        reference_data["lat"] = lat
        reference_data["lon"] = lon
        reference_data["alt"] = alt
        reference_data["active"] = True

        print("HSV activé par touche ou bouton.")
        print(f"→ Lat: {lat:.6f}")
        print(f"→ Lon: {lon:.6f}")
        print(f"→ Alt: {alt:.2f} ft")

    except Exception as e:
        print("Erreur lors de l’activation HSV :", e)

# Lier touche F
def on_key(event):
    if event.keysym.lower() == activation_key:
        activer_hsv()
root.bind("<Key>", on_key)

# Bouton au cas où
btn = tk.Button(root, text="Activer HSV (F)", command=activer_hsv)
btn.place(x=180, y=370)
btn_settings = tk.Button(root, text="⚙️ Paramètres", command=ouvrir_parametres)
btn_settings.place(x=300, y=370)

draw_reference_elements()
# Calcul distance entre deux GPS points
def latlon_to_meters(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def update_data():
    global last_x, last_y, last_alt_y

    error_count = 0
    max_errors = 3

    while True:
        try:
            lat = aq.get("PLANE_LATITUDE")
            lon = aq.get("PLANE_LONGITUDE")
            alt = aq.get("PLANE_ALTITUDE")

            if None in (lat, lon, alt):
                raise ValueError("Données SimConnect invalides (None)")

            error_count = 0

            print(f"Lat: {lat:.6f} | Lon: {lon:.6f} | Alt: {alt:.2f}")

            if reference_data["active"]:
                dx = latlon_to_meters(reference_data["lat"], reference_data["lon"], lat, reference_data["lon"])
                dy = latlon_to_meters(reference_data["lat"], reference_data["lon"], reference_data["lat"], lon)

                dx *= -1 if lat < reference_data["lat"] else 1
                dy *= -1 if lon < reference_data["lon"] else 1

                scale = max(circles_meters)  # s’adapte automatiquement à la portée max
                x = max(-1, min(1, dx / scale))
                y = max(-1, min(1, dy / scale))

                if abs(dx) > scale or abs(dy) > scale:
                    print("⚠️ Dérive > 10m (hors zone)")

                target_x = circle_center[0] + x * circle_radius
                target_y = circle_center[1] + y * circle_radius

                last_x += (target_x - last_x) * 0.2
                last_y += (target_y - last_y) * 0.2

                canvas.coords(
                    horiz_point,
                    last_x - 5, last_y - 5,
                    last_x + 5, last_y + 5
                )

                # Altitude
                alt_diff = alt - reference_data["alt"]
                scale_alt = 65
                offset = max(-1, min(1, alt_diff / scale_alt))
                bar_center = (bar_top + bar_bottom) / 2
                target_alt_y = bar_center - offset * 100

                last_alt_y += (target_alt_y - last_alt_y) * 0.2

                canvas.coords(
                    alt_point,
                    bar_x - 4, last_alt_y - 4,
                    bar_x + 4, last_alt_y + 4
                )

        except Exception as e:
            error_count += 1
            print(f"Erreur ({error_count}/{max_errors}) : {e}")
            if error_count >= max_errors:
                print("Trop d’erreurs consécutives, arrêt du script.")
                break

        time.sleep(0.05)

thread = threading.Thread(target=update_data, daemon=True)
thread.start()
root.mainloop()

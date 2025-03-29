import time
import threading
from SimConnect import *
import tkinter as tk
import math
import json
import os
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import keyboard

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
    "aligned": "green",
    "grid": "#ddd",
    "altitude_threshold": "#888"
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

activation_key = "f"
circles_meters = []
altitude_range = 40
tolerance_horizontal = 1.0
tolerance_vertical = 1.0
reference_data = {"lat": None, "lon": None, "alt": None, "hdg": 0.0, "active": False}

sm = SimConnect()
aq = AircraftRequests(sm, _time=200)

root = tk.Tk()
root.title("HSV - Helicopter Stabilisation Visualisator")
root.geometry("500x420")
root.resizable(False, False)
canvas = tk.Canvas(root, width=500, height=400, bg=COLORS["bg"])
canvas.pack()

circle_center = (150, 200)
circle_radius = 100
bar_top = 100
bar_bottom = 300
bar_x = 400

rosace = Image.new("RGBA", (200, 200), (255, 255, 255, 0))
draw = ImageDraw.Draw(rosace)
draw.ellipse((0, 0, 200, 200), outline=COLORS["circle_line"])
draw.line((100, 0, 100, 200), fill=COLORS["circle_line"])
draw.line((0, 100, 200, 100), fill=COLORS["circle_line"])
draw.text((95, 5), "N", fill=COLORS["label_text"])
rosace_img = ImageTk.PhotoImage(rosace)
rosace_id = canvas.create_image(circle_center[0], circle_center[1], image=rosace_img)

helico_raw = Image.open("assets/helico.png").resize((30, 30))
helico_img = ImageTk.PhotoImage(helico_raw)
helico_img_id = canvas.create_image(circle_center[0], circle_center[1], image=helico_img)

horiz_point = canvas.create_oval(0, 0, 0, 0, fill=COLORS["horizontal_point"])
alt_point = canvas.create_oval(0, 0, 0, 0, fill=COLORS["altitude_point"])

# Lignes de seuil de tolérance altitude
alt_thresh_upper = canvas.create_line(bar_x - 10, 0, bar_x + 10, 0, fill=COLORS["altitude_threshold"], dash=(2, 2))
alt_thresh_lower = canvas.create_line(bar_x - 10, 0, bar_x + 10, 0, fill=COLORS["altitude_threshold"], dash=(2, 2))

last_x, last_y = circle_center
last_alt_y = (bar_top + bar_bottom) / 2

drawn_graduations = []
drawn_labels = []

def global_hotkey_listener():
    while True:
        try:
            if keyboard.is_pressed(activation_key):
                activer_hsv()
                time.sleep(0.5)  # anti-spam
        except:
            pass
        time.sleep(0.05)
threading.Thread(target=global_hotkey_listener, daemon=True).start()

def latlon_to_meters(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def bearing_to(lat1, lon1, lat2, lon2):
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def update_data():
    global last_x, last_y, last_alt_y, rosace_img
    while True:
        try:
            lat = aq.get("PLANE_LATITUDE")
            lon = aq.get("PLANE_LONGITUDE")
            alt = aq.get("PLANE_ALTITUDE")
            hdg_raw = aq.get("PLANE_HEADING_DEGREES_TRUE")

            try:
                hdg = float(str(hdg_raw).replace(",", "."))
                if 0.0 <= hdg <= 6.3:
                    hdg = math.degrees(hdg)
                hdg = hdg % 360
            except:
                hdg = 0.0
                print(f"[ERREUR] Heading invalide : {repr(hdg_raw)}")

            if reference_data["active"]:
                bearing = bearing_to(lat, lon, reference_data["lat"], reference_data["lon"])
                rel_angle = (bearing - hdg + 360) % 360

                distance = latlon_to_meters(lat, lon, reference_data["lat"], reference_data["lon"])
                max_d = max(circles_meters)
                d_norm = min(1, distance / max_d)

                angle_rad = math.radians(rel_angle)
                x_rot = math.sin(angle_rad) * d_norm
                y_rot = math.cos(angle_rad) * d_norm

                target_x = circle_center[0] + x_rot * circle_radius
                target_y = circle_center[1] - y_rot * circle_radius
                last_x += (target_x - last_x) * 0.2
                last_y += (target_y - last_y) * 0.2

                aligned_pos = distance < tolerance_horizontal
                canvas.coords(horiz_point, last_x - 5, last_y - 5, last_x + 5, last_y + 5)
                canvas.itemconfig(horiz_point, fill=COLORS["aligned"] if aligned_pos else COLORS["horizontal_point"])

                rosace_rot = rosace.rotate(hdg, resample=Image.BICUBIC)
                rosace_img = ImageTk.PhotoImage(rosace_rot)
                canvas.itemconfig(rosace_id, image=rosace_img)
                canvas.image = rosace_img

                canvas.itemconfig(helico_img_id, image=helico_img)
                canvas.image2 = helico_img

                alt_diff = alt - reference_data["alt"]
                offset = max(-1, min(1, alt_diff / altitude_range))
                bar_center = (bar_top + bar_bottom) / 2
                target_alt_y = bar_center - offset * 100
                last_alt_y += (target_alt_y - last_alt_y) * 0.2

                aligned_alt = abs(alt_diff) < tolerance_vertical
                canvas.coords(alt_point, bar_x - 4, last_alt_y - 4, bar_x + 4, last_alt_y + 4)
                canvas.itemconfig(alt_point, fill=COLORS["aligned"] if aligned_alt else COLORS["altitude_point"])

                # Affichage des lignes de seuil
                offset_thresh = (tolerance_vertical / altitude_range) * 100
                canvas.coords(alt_thresh_upper, bar_x - 10, bar_center - offset_thresh, bar_x + 10, bar_center - offset_thresh)
                canvas.coords(alt_thresh_lower, bar_x - 10, bar_center + offset_thresh, bar_x + 10, bar_center + offset_thresh)

        except Exception as e:
            print("Erreur update:", e)
        time.sleep(0.05)

def activer_hsv():
    try:
        lat = aq.get("PLANE_LATITUDE")
        lon = aq.get("PLANE_LONGITUDE")
        alt = aq.get("PLANE_ALTITUDE")
        hdg = aq.get("PLANE_HEADING_DEGREES_TRUE")

        try:
            hdg = float(str(hdg).replace(",", "."))
            if 0.0 <= hdg <= 6.3:
                hdg = math.degrees(hdg)
            hdg = hdg % 360
        except:
            hdg = 0.0

        if None in (lat, lon, alt):
            return
        reference_data.update({"lat": lat, "lon": lon, "alt": alt, "hdg": hdg, "active": True})
    except Exception as e:
        print("Erreur HSV:", e)

def on_key(event):
    if event.keysym.lower() == activation_key:
        activer_hsv()

def draw_reference_elements():
    for el in drawn_graduations + drawn_labels:
        canvas.delete(el)
    drawn_graduations.clear()
    drawn_labels.clear()

    max_m = max(circles_meters)
    for i in range(-2, 3):
        offset = i * (circle_radius / 2)
        drawn_graduations.append(canvas.create_line(circle_center[0] + offset, circle_center[1] - circle_radius,
                                                     circle_center[0] + offset, circle_center[1] + circle_radius, fill=COLORS["grid"]))
        drawn_graduations.append(canvas.create_line(circle_center[0] - circle_radius, circle_center[1] + offset,
                                                     circle_center[0] + circle_radius, circle_center[1] + offset, fill=COLORS["grid"]))

    for m in circles_meters:
        scale = m / max_m
        drawn_graduations.append(canvas.create_oval(
            circle_center[0] - circle_radius * scale,
            circle_center[1] - circle_radius * scale,
            circle_center[0] + circle_radius * scale,
            circle_center[1] + circle_radius * scale,
            outline=COLORS["circle_line"], dash=(2, 2)))
        drawn_labels.append(canvas.create_text(circle_center[0] + circle_radius * scale + 10, circle_center[1],
                                               text=f"{m}m", font=("Arial", 8), fill=COLORS["label_text"]))

    for i in range(-2, 3):
        val = i * (altitude_range // 2)
        y = (bar_top + bar_bottom) / 2 - (val / altitude_range) * 100
        drawn_graduations.append(canvas.create_line(bar_x - 10, y, bar_x + 10, y, fill=COLORS["graduation"]))
        drawn_labels.append(canvas.create_text(bar_x + 25, y, text=f"{val:+} ft", font=("Arial", 9)))

def ouvrir_parametres():
    top = tk.Toplevel(root)
    top.title("Paramètres HSV")
    top.geometry("300x300")

    entries = {}
    labels = [
        ("Touche activation HSV", activation_key, "activation_key"),
        ("Cercles (en mètres, séparés par des virgules)", ", ".join(map(str, circles_meters)), "circles"),
        ("Échelle altitude (±x ft)", str(altitude_range), "alt_range"),
        ("Tolérance position (m)", str(tolerance_horizontal), "tol_pos"),
        ("Tolérance altitude (ft)", str(tolerance_vertical), "tol_alt")
    ]

    for label_text, default, key in labels:
        tk.Label(top, text=label_text).pack()
        entry = tk.Entry(top)
        entry.insert(0, default)
        entry.pack()
        entries[key] = entry

    def sauvegarder():
        try:
            new_settings = {
                "activation_key": entries["activation_key"].get().strip().lower(),
                "circles_meters": list(map(float, entries["circles"].get().split(","))),
                "altitude_range": int(entries["alt_range"].get()),
                "alignment_tolerance": {
                    "horizontal_m": float(entries["tol_pos"].get()),
                    "vertical_ft": float(entries["tol_alt"].get())
                }
            }
            with open(SETTINGS_FILE, "w") as f:
                json.dump(new_settings, f, indent=4)
            messagebox.showinfo("Succès", "Paramètres sauvegardés.")
            load_settings()
            top.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

    tk.Button(top, text="Sauvegarder", command=sauvegarder).pack(pady=10)

def load_settings():
    global activation_key, circles_meters, altitude_range, tolerance_horizontal, tolerance_vertical
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    with open(SETTINGS_FILE, "r") as f:
        s = json.load(f)
    activation_key = s.get("activation_key", "f")
    circles_meters = s.get("circles_meters", [2, 5, 10])
    altitude_range = s.get("altitude_range", 40)
    tolerance_horizontal = s["alignment_tolerance"]["horizontal_m"]
    tolerance_vertical = s["alignment_tolerance"]["vertical_ft"]
    draw_reference_elements()

load_settings()
root.bind("<Key>", on_key)
tk.Button(root, text="Activer HSV (F)", command=activer_hsv).place(x=180, y=370)
tk.Button(root, text="⚙️ Paramètres", command=ouvrir_parametres).place(x=300, y=370)
threading.Thread(target=update_data, daemon=True).start()
root.mainloop()

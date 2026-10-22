import tkinter as tk
from tkinter import ttk
import random
import math
import time

# ---------------- Window Setup ----------------
root = tk.Tk()
root.title("Ride Matching — Clean Version")
root.geometry("860x650")
root.config(bg="#f5f5f5")

# ---------------- Canvas (Map) ----------------
canvas = tk.Canvas(root, width=650, height=450, bg="white", relief="solid", bd=2)
canvas.pack(pady=15, side=tk.LEFT)

# ---------------- Right Panel ----------------
panel = tk.Frame(root, bg="#f5f5f5")
panel.pack(padx=10, pady=15, side=tk.LEFT, fill=tk.Y)

status_label = tk.Label(
    panel,
    text="Generate drivers & passengers to begin.",
    font=("Arial", 11),
    fg="black",
    bg="#f5f5f5",
    wraplength=180,
    justify=tk.LEFT
)
status_label.pack(pady=5)

# ---------------- Variables ----------------
drivers = []
passengers = []
matches = []

# -------- Fare / Distance Scale --------
PIXELS_PER_KM = 80
BASE_FARE = 30
PER_KM_RATE = 12

# ---------------- Match Table ----------------
cols = ("match", "pair", "distance", "fare")
tree = ttk.Treeview(panel, columns=cols, show="headings", height=18)
tree.heading("match", text="Match #")
tree.heading("pair", text="Pair")
tree.heading("distance", text="Distance (km)")
tree.heading("fare", text="Fare")

tree.column("match", width=60, anchor="center")
tree.column("pair", width=90, anchor="center")
tree.column("distance", width=100, anchor="center")
tree.column("fare", width=80, anchor="e")

tree.pack(pady=10)

# ---------------- Generate Data ----------------
def generate_data():
    global drivers, passengers, matches

    canvas.delete("all")
    tree.delete(*tree.get_children())
    matches = []

    drivers = [(random.randint(50, 600), random.randint(60, 380)) for _ in range(5)]
    passengers = [(random.randint(50, 600), random.randint(60, 380)) for _ in range(5)]

    for idx, (x, y) in enumerate(drivers, start=1):
        canvas.create_oval(x-6, y-6, x+6, y+6, fill="blue")
        canvas.create_text(x, y-12, text=f"D{idx}", font=("Arial", 8))

    for idx, (x, y) in enumerate(passengers, start=1):
        canvas.create_oval(x-6, y-6, x+6, y+6, fill="red")
        canvas.create_text(x, y-12, text=f"P{idx}", font=("Arial", 8))

    status_label.config(text="Drivers and passengers placed. Click 'Find Rides'.")

# ---------------- Match Logic ----------------
def match_rides():
    global matches

    if not drivers or not passengers:
        status_label.config(text="Generate data first!")
        return

    tree.delete(*tree.get_children())
    matches = []
    used = set()

    for p_idx, (px, py) in enumerate(passengers, start=1):
        best = None
        best_dist = float("inf")

        for d_idx, (dx, dy) in enumerate(drivers, start=1):
            if d_idx in used:
                continue

            dist = math.hypot(px - dx, py - dy)
            if dist < best_dist:
                best_dist = dist
                best = (d_idx, dx, dy)

        if best:
            d_idx, dx, dy = best
            used.add(d_idx)
            matches.append((p_idx, d_idx, (px, py), (dx, dy), best_dist))

    animate_matches()

# ---------------- Animate Lines Only ----------------
def animate_matches():
    total_fare = 0
    tree.delete(*tree.get_children())

    for i, (p_idx, d_idx, (px, py), (dx, dy), dist_px) in enumerate(matches, start=1):

        dist_km = dist_px / PIXELS_PER_KM
        fare = round(BASE_FARE + PER_KM_RATE * dist_km, 2)
        total_fare += fare

        # --- animate only the green line (NO TEXT ON MAP) ---
        line = canvas.create_line(dx, dy, dx, dy, fill="green", width=3)
        for step in range(1, 21):
            x = dx + (px - dx) * step / 20
            y = dy + (py - dy) * step / 20
            canvas.coords(line, dx, dy, x, y)
            canvas.update()
            time.sleep(0.02)

        # Add to side table (NOT on map)
        tree.insert(
            "",
            tk.END,
            values=(
                i,
                f"P{p_idx}-D{d_idx}",
                f"{dist_km:.2f}",
                f"₹{fare:.2f}"
            )
        )

    status_label.config(text=f"Matched {len(matches)} rides. Total Fare: ₹{total_fare:.2f}")

# ---------------- Buttons ----------------
btn1 = tk.Button(panel, text="Generate Drivers & Passengers",
                 bg="#90EE90", font=("Arial", 11), width=30, command=generate_data)
btn1.pack(pady=5)

btn2 = tk.Button(panel, text="Find Rides (Match)",
                 bg="#ADD8E6", font=("Arial", 11), width=30, command=match_rides)
btn2.pack(pady=5)

btn3 = tk.Button(panel, text="Exit",
                 bg="#FFB6C1", font=("Arial", 11), width=30, command=root.destroy)
btn3.pack(pady=5)

root.mainloop()


# simple_delivery_planner.py
# Simple delivery planner: Cart + Delivery Type + Random stops + Shortest route + ETA on map
# Run: python simple_delivery_planner.py
# Requires: Python 3.x (tkinter standard)

import tkinter as tk
from tkinter import ttk
import random, math
from functools import lru_cache

# ---------- Simple map coordinates ----------
WAREHOUSE_POS = (100, 100)
USER_POS = (520, 360)
PIXELS_TO_KM = 1/80.0  # 80 pixels ~ 1 km

# Speed estimates (km/h) and service time
SPEED = {"Express": 50.0, "Standard": 40.0, "Grouped": 35.0}
SERVICE_MIN_PER_STOP = 3.0
OVERHEAD_MIN = 7.0  # fixed overhead for processing

# ---------- Products ----------
PRODUCTS = ["Books", "Pens", "Pencils", "Graphpaper", "Notebooks", "Markers"]

# ---------- Helper functions ----------
def euclid(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def px_to_km(px):
    return px * PIXELS_TO_KM

def estimate_minutes(total_px, delivery_type, stops_count):
    total_km = px_to_km(total_px)
    speed = SPEED.get(delivery_type, 40.0)
    travel_min = (total_km / speed) * 60.0
    service = stops_count * SERVICE_MIN_PER_STOP
    return round(travel_min + service + OVERHEAD_MIN, 1)

# DP TSP (bitmask memoized) for small n
def tsp_dp(dist):
    n = len(dist)
    ALL = (1 << n) - 1

    @lru_cache(None)
    def visit(pos, mask):
        if mask == ALL:
            return 0.0, []
        best_cost = float('inf'); best_path = []
        for nxt in range(n):
            if (mask >> nxt) & 1:
                continue
            c_sub, p_sub = visit(nxt, mask | (1 << nxt))
            cand = dist[pos][nxt] + c_sub
            if cand < best_cost:
                best_cost = cand
                best_path = [nxt] + p_sub
        return best_cost, best_path

    cost, path = visit(0, 1 << 0)
    return cost, [0] + path

# Greedy nearest-neighbor fallback
def tsp_greedy(dist):
    n = len(dist)
    visited = [False] * n
    cur = 0
    visited[0] = True
    route = [0]
    total = 0.0
    for _ in range(n - 1):
        best = None; bestd = float('inf')
        for j in range(n):
            if not visited[j] and dist[cur][j] < bestd:
                bestd = dist[cur][j]; best = j
        if best is None:
            break
        visited[best] = True
        total += bestd
        route.append(best)
        cur = best
    return total, route

def build_dist(points):
    n = len(points)
    d = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            d[i][j] = euclid(points[i], points[j])
    return d

def generate_random_stops(delivery_type):
    if delivery_type == "Express":
        return []
    elif delivery_type == "Standard":
        k = random.randint(1, 3)
    else:
        k = random.randint(2, 6)
    stops = []
    for i in range(k):
        t = (i+1)/(k+1)
        x = int(WAREHOUSE_POS[0] + (USER_POS[0]-WAREHOUSE_POS[0])*t + random.randint(-40, 40))
        y = int(WAREHOUSE_POS[1] + (USER_POS[1]-WAREHOUSE_POS[1])*t + random.randint(-40, 40))
        stops.append((x, y))
    return stops

# ---------- GUI ----------
class SimplePlanner:
    def __init__(self, root):
        self.root = root
        root.title("Simple Delivery Planner")
        root.geometry("1000x620")
        self.canvas = tk.Canvas(root, width=680, height=520, bg="white", bd=2, relief="solid")
        self.canvas.place(x=10, y=10)

        panel = tk.Frame(root)
        panel.place(x=700, y=10, width=280, height=520)

        # Cart (listbox + add/remove)
        tk.Label(panel, text="Cart (select products then Add):").pack(anchor="w", pady=(6,0), padx=6)
        self.prod_list = tk.Listbox(panel, selectmode=tk.MULTIPLE, height=6)
        for p in PRODUCTS:
            self.prod_list.insert(tk.END, p)
        self.prod_list.pack(fill="x", padx=6)

        btn_frame = tk.Frame(panel)
        btn_frame.pack(fill="x", padx=6, pady=6)
        ttk.Button(btn_frame, text="Add to Cart", command=self.add_to_cart).pack(side="left", expand=True, fill="x")
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_from_cart).pack(side="left", expand=True, fill="x", padx=(6,0))

        tk.Label(panel, text="Cart:").pack(anchor="w", padx=6)
        self.cart_box = tk.Listbox(panel, height=6)
        self.cart_box.pack(fill="x", padx=6)

        # Delivery type
        tk.Label(panel, text="Delivery Type:").pack(anchor="w", pady=(8,0), padx=6)
        self.type_var = tk.StringVar(value="Standard")
        self.type_dd = ttk.Combobox(panel, values=["Express","Standard","Grouped"], textvariable=self.type_var, state="readonly")
        self.type_dd.pack(fill="x", padx=6)

        # Plan button ONLY (Estimate Time button intentionally removed)
        ttk.Button(panel, text="Plan Delivery", command=self.plan_delivery).pack(fill="x", padx=6, pady=(12,6))

        # Info area
        tk.Label(panel, text="Info:").pack(anchor="w", padx=6, pady=(8,0))
        self.info = tk.Text(panel, height=15, wrap="word")
        self.info.pack(fill="both", padx=6, pady=(0,6), expand=True)

        self.draw_base()

    def add_to_cart(self):
        sel = self.prod_list.curselection()
        for i in sel:
            item = self.prod_list.get(i)
            self.cart_box.insert(tk.END, item)

    def remove_from_cart(self):
        sel = list(self.cart_box.curselection())
        for i in reversed(sel):
            self.cart_box.delete(i)

    def draw_base(self):
        self.canvas.delete("all")
        wx, wy = WAREHOUSE_POS
        self.canvas.create_oval(wx-12, wy-12, wx+12, wy+12, fill="blue", tags="warehouse")
        self.canvas.create_text(wx, wy+20, text="Warehouse", tags="warehouse_label")
        ux, uy = USER_POS
        self.canvas.create_rectangle(ux-10, uy-10, ux+10, uy+10, fill="red", tags="user")
        self.canvas.create_text(ux, uy+20, text="Your Location", tags="user_label")
        self.canvas.create_rectangle(2,2,678,518, tags="border")

    def plan_delivery(self):
        self.draw_base()
        delivery_type = self.type_var.get()
        cart_items = list(self.cart_box.get(0, tk.END))
        if not cart_items:
            self.info.delete(1.0, tk.END)
            self.info.insert(tk.END, "Cart empty. Add items before planning.\n")
            return

        stops = generate_random_stops(delivery_type)
        points = [WAREHOUSE_POS] + stops + [USER_POS]
        dist_matrix = build_dist(points)
        n = len(points)

        # compute route and cost (pixels)
        if n <= 12:
            cost_px, route = tsp_dp(dist_matrix)
        else:
            cost_px, route = tsp_greedy(dist_matrix)

        # ensure route ends at user (index n-1)
        if route[-1] != n-1:
            cost_px += dist_matrix[route[-1]][n-1]
            route.append(n-1)

        # draw stops (unlabeled)
        for s in stops:
            self.canvas.create_oval(s[0]-4, s[1]-4, s[0]+4, s[1]+4, fill="grey", tags="stop")

        # draw route
        for a, b in zip(route, route[1:]):
            p1 = points[a]; p2 = points[b]
            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], width=3, fill="green", tags="route")

        # compute ETA and display it on canvas and info box
        stops_count = max(0, len(stops)) + 1  # service at final user + stops
        est_min = estimate_minutes(cost_px, delivery_type, stops_count)

        # info update
        self.info.delete(1.0, tk.END)
        self.info.insert(tk.END, f"Cart items: {', '.join(cart_items)}\n")
        self.info.insert(tk.END, f"Delivery type: {delivery_type}\n")
        self.info.insert(tk.END, f"Number of stops: {len(stops)}\n")
        self.info.insert(tk.END, f"Route order (indices): {route}\n")
        self.info.insert(tk.END, f"Approx distance: {px_to_km(cost_px):.2f} km\n")
        self.info.insert(tk.END, f"Estimated delivery time: ~ {est_min} minutes\n")

        # show ETA on canvas near route centroid
        midx = sum(p[0] for p in points) // len(points)
        midy = sum(p[1] for p in points) // len(points)
        self.canvas.delete("eta")
        self.canvas.create_text(midx, midy, text=f"ETA: ~ {est_min} min", font=("Arial", 12, "bold"), fill="black", tags="eta")

# ---------- Run ----------
if __name__ == "__main__":
    random.seed()
    root = tk.Tk()
    app = SimplePlanner(root)
    root.mainloop()

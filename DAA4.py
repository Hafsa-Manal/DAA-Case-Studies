import tkinter as tk
from tkinter import ttk
import time, heapq

CELL = 60
MARGIN = 20

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(start, goal, rows, cols, obstacles):
    open_set = []
    heapq.heappush(open_set, (manhattan(start, goal), 0, start, None))
    came = {}
    gscore = {start: 0}
    while open_set:
        f, g, current, parent = heapq.heappop(open_set)
        if current in came:
            continue
        came[current] = parent
        if current == goal:
            path = []
            cur = current
            while cur is not None:
                path.append(cur)
                cur = came[cur]
            return path[::-1]
        r, c = current
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            nb = (nr, nc)
            if 0 <= nr < rows and 0 <= nc < cols and nb not in obstacles:
                tg = g + 1
                if tg < gscore.get(nb, float("inf")):
                    gscore[nb] = tg
                    heapq.heappush(open_set, (tg + manhattan(nb, goal), tg, nb, current))
    return None

def snake_order(rows, cols, obstacles):
    order = []
    for r in range(rows):
        rng = range(cols) if r % 2 == 0 else range(cols - 1, -1, -1)
        for c in rng:
            if (r, c) not in obstacles:
                order.append((r, c))
    return order

def path_from_order(start, order, rows, cols, obstacles):
    path = []
    current = start
    if current not in obstacles:
        path.append(current)
    for target in order:
        if target == current:
            continue
        p = astar(current, target, rows, cols, obstacles)
        if p is None:
            continue
        if not path:
            path.extend(p)
        else:
            path.extend(p[1:])
        current = target
    return path

class SimpleRobotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Task Manager")
        self.rows = 6
        self.cols = 6
        self.robot = (0, 0)
        self.furniture = set()
        self.target = None
        self.running = False
        self.dirty = set()
        self._anim_path = []
        self._anim_index = 0
        self._anim_remove_target = None
        self.build_ui()
        self.reset_grid()
        self.draw_static()
        self.draw_robot()

    def build_ui(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        ttk.Button(left, text="1. Clean (Full)", command=self.clean_full).pack(fill="x", pady=4)
        ttk.Button(left, text="2. Quick Clean", command=self.quick_clean).pack(fill="x", pady=4)
        ttk.Button(left, text="3. Spot Clean", command=self.start_spot_clean).pack(fill="x", pady=4)
        ttk.Button(left, text="Reset", command=self.reset_all).pack(fill="x", pady=4)
        ttk.Label(left, text="Click on grid to place/remove furniture").pack(pady=10)
        self.log = tk.Text(left, width=32, height=16)
        self.log.pack()
        right = ttk.Frame(self)
        right.pack(side="right", expand=True, fill="both")
        self.canvas = tk.Canvas(right, bg="white")
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Button-1>", self.on_click)

    def log_msg(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def cell_from_xy(self, x, y):
        c = (x - MARGIN) // CELL
        r = (y - MARGIN) // CELL
        r, c = int(r), int(c)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    def reset_grid(self):
        self.robot = (0, 0)
        self.furniture.clear()
        self.target = None
        self.dirty = {(r, c) for r in range(self.rows) for c in range(self.cols)}
        if self.robot in self.dirty:
            self.dirty.remove(self.robot)

    def draw_static(self):
        self.canvas.delete("bg")
        for r in range(self.rows):
            for c in range(self.cols):
                x0 = MARGIN + c * CELL
                y0 = MARGIN + r * CELL
                x1 = x0 + CELL
                y1 = y0 + CELL
                fill = "lightgrey" if (r, c) in self.dirty else "white"
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="#bbb", fill=fill, tags="bg")
                if (r, c) in self.furniture:
                    self.canvas.create_rectangle(x0 + 8, y0 + 8, x1 - 8, y1 - 8, fill="black", tags="bg")
                if self.target == (r, c):
                    self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="T", font=("Arial", 14, "bold"), tags="bg")

    def draw_robot(self):
        self.canvas.delete("robot")
        r, c = self.robot
        x = MARGIN + c * CELL + CELL / 2
        y = MARGIN + r * CELL + CELL / 2
        self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="blue", tags="robot")

    def on_click(self, event):
        if self.running:
            return
        pos = self.cell_from_xy(event.x, event.y)
        if pos is None:
            return
        if pos == self.robot:
            self.log_msg("Cannot place furniture on robot.")
            return
        if pos in self.furniture:
            self.furniture.remove(pos)
            self.dirty.add(pos)
            self.log_msg(f"Removed furniture {pos}")
        else:
            self.furniture.add(pos)
            if pos in self.dirty:
                self.dirty.remove(pos)
            self.log_msg(f"Placed furniture {pos}")
        self.draw_static()
        self.draw_robot()

    def animate(self, path, remove_target=None):
        if not path:
            return
        self.running = True
        self._anim_path = list(path)
        self._anim_index = 0
        self._anim_remove_target = remove_target
        self.after(0, self._animate_step)

    def _animate_step(self):
        if not self.running or self._anim_index >= len(self._anim_path):
            self.running = False
            return
        step = self._anim_path[self._anim_index]
        self._anim_index += 1
        self.robot = step
        if step in self.dirty:
            self.dirty.remove(step)
        if self._anim_remove_target and step == self._anim_remove_target:
            if step in self.dirty:
                self.dirty.remove(step)
            self.target = None
        self.draw_static()
        self.draw_robot()
        self.after(100, self._animate_step)

    def find_hamiltonian_cycle(self, rows, cols, start=(0, 0), obstacles=None, time_limit=1.0):
        obstacles = obstacles or set()
        N = rows * cols - len(obstacles)
        visited = set()
        path = []
        start_time = time.time()
        def neighbors(u):
            r, c = u
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols and (rr, cc) not in obstacles:
                    yield (rr, cc)
        if start in obstacles:
            return None
        visited.add(start)
        path.append(start)
        def backtrack(u):
            if time.time() - start_time > time_limit:
                return False
            if len(path) == N:
                for nb in neighbors(path[-1]):
                    if nb == start:
                        return True
                return False
            nbrs = [v for v in neighbors(u) if v not in visited]
            nbrs.sort(key=lambda v: sum(1 for _ in neighbors(v)))
            for v in nbrs:
                visited.add(v)
                path.append(v)
                if backtrack(v):
                    return True
                path.pop()
                visited.remove(v)
            return False
        if backtrack(start):
            return path
        return None

    def plan_full_path(self):
        obstacles = set(self.furniture)
        ham = self.find_hamiltonian_cycle(self.rows, self.cols, start=self.robot, obstacles=obstacles)
        if ham:
            order = ham
        else:
            order = snake_order(self.rows, self.cols, obstacles)
        path = path_from_order(self.robot, order, self.rows, self.cols, obstacles)
        return path

    def clean_full(self):
        if self.running:
            return
        self.log_msg("Clean: full coverage avoiding furniture.")
        path = self.plan_full_path()
        self.animate(path)

    def quick_clean(self):
        if self.running:
            return
        self.log_msg("Quick Clean: same as full clean.")
        path = self.plan_full_path()
        self.animate(path)

    def start_spot_clean(self):
        if self.running:
            return
        self.reset_grid()
        self.draw_static()
        self.draw_robot()
        self.log_msg("Grid fully reset for Spot Clean. Click a tile to clean it.")
        self.canvas.bind("<Button-1>", self.select_spot)

    def select_spot(self, event):
        self.canvas.bind("<Button-1>", self.on_click)
        pos = self.cell_from_xy(event.x, event.y)
        if pos is None:
            return
        self.target = pos
        self.log_msg(f"Spot selected: {pos}")
        self.draw_static()
        self.draw_robot()
        obstacles = set(self.furniture)
        obstacles.discard(pos)
        path = astar(self.robot, pos, self.rows, self.cols, obstacles)
        if not path:
            self.log_msg("No path to target.")
            self.target = None
            return
        self.animate(path, remove_target=pos)

    def reset_all(self):
        if self.running:
            return
        self.reset_grid()
        self.draw_static()
        self.draw_robot()
        self.log_msg("Reset complete.")

if __name__ == "__main__":
    SimpleRobotApp().mainloop()

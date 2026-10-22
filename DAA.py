import tkinter as tk
import random
import math
import heapq
import time

root = tk.Tk()
root.title("Divide & Conquer and Greedy Algorithms Visual Demo")
root.geometry("700x600")

canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 11), fg="blue")
result_label.pack(pady=5)


# ---------------------- 1. Closest Pair of Points (Uber/Ola) ----------------------
def closest_pair():
    canvas.delete("all")
    drivers = [(random.randint(30, 570), random.randint(30, 370)) for _ in range(5)]
    passengers = [(random.randint(30, 570), random.randint(30, 370)) for _ in range(5)]

    for x, y in drivers:
        canvas.create_oval(x-6, y-6, x+6, y+6, fill="blue")
    for x, y in passengers:
        canvas.create_oval(x-6, y-6, x+6, y+6, fill="red")

    # Animate matching
    for p in passengers:
        nearest = min(drivers, key=lambda d: math.sqrt((p[0]-d[0])**2 + (p[1]-d[1])**2))
        line = canvas.create_line(p[0], p[1], p[0], p[1], fill="green", width=2)
        for i in range(10):
            x = p[0] + (nearest[0]-p[0]) * i/10
            y = p[1] + (nearest[1]-p[1]) * i/10
            canvas.coords(line, p[0], p[1], x, y)
            canvas.update()
            time.sleep(0.05)
    result_label.config(text="Closest Pair: Green lines connect passengers to nearest drivers.")


# ---------------------- 2. Job Sequencing with Deadlines (Cloud Scheduling) ----------------------
def job_sequencing():
    canvas.delete("all")

    jobs = [('A', 2, 100), ('B', 1, 19), ('C', 2, 27), ('D', 1, 25), ('E', 3, 15)]
    jobs.sort(key=lambda x: x[2], reverse=True)
    max_deadline = max(j[1] for j in jobs)
    slots = ['-1'] * max_deadline

    canvas.create_text(300, 30, text="Job Sequencing with Deadlines", font=("Arial", 14, "bold"))

    # Animate scheduling process
    for job in jobs:
        for j in range(job[1]-1, -1, -1):
            if slots[j] == '-1':
                slots[j] = job[0]
                color = random.choice(["#FFD700", "#FFA07A", "#98FB98", "#87CEFA"])
                x = 100 + j*150
                rect = canvas.create_rectangle(x, 200, x+100, 250, fill=color, outline="black")
                canvas.create_text(x+50, 225, text=job[0], font=("Arial", 12, "bold"))
                canvas.update()
                time.sleep(0.5)
                break

    result_label.config(text="Job Sequencing: Jobs placed in slots to maximize profit.")


# ---------------------- 3. Minimum Cost Spanning Tree (Telecom Network) ----------------------
def mst_kruskal():
    canvas.delete("all")

    # Simple graph setup
    positions = {'A': (150, 100), 'B': (450, 100), 'C': (150, 300), 'D': (450, 300)}
    edges = [
        ('A', 'B', 2),
        ('A', 'C', 3),
        ('B', 'D', 3),
        ('C', 'D', 2),
        ('B', 'C', 4)
    ]
    edges.sort(key=lambda x: x[2])

    parent = {v: v for v in positions}

    def find(u):
        while parent[u] != u:
            u = parent[u]
        return u

    def union(u, v):
        parent[find(u)] = find(v)

    # Draw all nodes and edges
    for u, v, w in edges:
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        canvas.create_line(x1, y1, x2, y2, fill="gray", dash=(3, 3))
        canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(w), font=("Arial", 10))

    for n, (x, y) in positions.items():
        canvas.create_oval(x-15, y-15, x+15, y+15, fill="lightblue")
        canvas.create_text(x, y, text=n, font=("Arial", 12, "bold"))

    # Animate MST creation
    for u, v, w in edges:
        if find(u) != find(v):
            union(u, v)
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            for i in range(10):
                canvas.create_line(x1, y1, x1 + (x2 - x1)*i/10, y1 + (y2 - y1)*i/10, fill="green", width=3)
                canvas.update()
                time.sleep(0.05)

    result_label.config(text="MST (Kruskal’s): Green lines = minimum cost connections.")


# ---------------------- 4. Dijkstra’s Algorithm (Google Maps) ----------------------
def dijkstra():
    canvas.delete("all")

    positions = {'A': (100, 200), 'B': (250, 100), 'C': (250, 300), 'D': (400, 200)}
    graph = {
        'A': {'B': 2, 'C': 4},
        'B': {'D': 7, 'C': 1},
        'C': {'D': 3},
        'D': {}
    }

    start = 'A'
    pq = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    # Draw graph
    for u in graph:
        for v, w in graph[u].items():
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            canvas.create_line(x1, y1, x2, y2, fill="gray")
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(w), fill="black")

    for n, (x, y) in positions.items():
        canvas.create_oval(x-15, y-15, x+15, y+15, fill="lightgreen")
        canvas.create_text(x, y, text=n, font=("Arial", 12, "bold"))

    # Animate Dijkstra shortest path discovery
    def dijkstra():
     canvas.delete("all")

    positions = {'A': (100, 200), 'B': (250, 100), 'C': (250, 300), 'D': (400, 200)}
    graph = {
        'A': {'B': 2, 'C': 4},
        'B': {'D': 7, 'C': 1},
        'C': {'D': 3},
        'D': {}
    }

    start = 'A'
    pq = [(0, start)]
    distances = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    distances[start] = 0

    # Draw graph
    for u in graph:
        for v, w in graph[u].items():
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            canvas.create_line(x1, y1, x2, y2, fill="gray")
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=str(w), fill="black")

    for n, (x, y) in positions.items():
        canvas.create_oval(x-15, y-15, x+15, y+15, fill="lightgreen")
        canvas.create_text(x, y, text=n, font=("Arial", 12, "bold"))

    # Dijkstra execution with animation
    visited = set()
    while pq:
        dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        # Highlight visiting node
        x, y = positions[node]
        canvas.create_oval(x-18, y-18, x+18, y+18, outline="red", width=2)
        canvas.update()
        time.sleep(0.4)

        for neighbor, weight in graph[node].items():
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))
                # Animate edge relaxation
                x1, y1 = positions[node]
                x2, y2 = positions[neighbor]
                canvas.create_line(x1, y1, x2, y2, fill="blue", width=3)
                canvas.update()
                time.sleep(0.3)

    # Draw final shortest-path tree in bold green
    for node, parent in prev.items():
        if parent:
            x1, y1 = positions[node]
            x2, y2 = positions[parent]
            canvas.create_line(x1, y1, x2, y2, fill="green", width=4)

    result_label.config(
        text="Dijkstra’s: Blue = exploring edges, Green = final shortest paths."
    )


# ---------------------- Buttons ----------------------
tk.Label(root, text="Select an Algorithm to Demonstrate:", font=("Arial", 13, "bold")).pack()

tk.Button(root, text="Closest Pair of Points (Uber/Ola)", command=closest_pair, bg="#90EE90", width=45).pack(pady=3)
tk.Button(root, text="Job Sequencing (Cloud Scheduling)", command=job_sequencing, bg="#FFDAB9", width=45).pack(pady=3)
tk.Button(root, text="Minimum Cost Spanning Tree (Telecom)", command=mst_kruskal, bg="#ADD8E6", width=45).pack(pady=3)
tk.Button(root, text="Dijkstra’s Algorithm (Google Maps)", command=dijkstra, bg="#FFB6C1", width=45).pack(pady=3)

root.mainloop()


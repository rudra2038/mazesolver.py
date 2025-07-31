import random
import matplotlib.pyplot as plt
from collections import deque
import time
import tracemalloc
import tkinter as tk
from tkinter import ttk, messagebox

# Maze generation and solving functions
def generate_maze(width, height):
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1
    maze = [["#" for _ in range(width)] for _ in range(height)]
    start_x, start_y = 1, 1
    maze[start_y][start_x] = "."
    directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

    def is_within_bounds(x, y):
        return 0 < x < width - 1 and 0 < y < height - 1

    def carve_passages(x, y):
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_within_bounds(nx, ny) and maze[ny][nx] == "#":
                maze[y + dy // 2][x + dx // 2] = "."
                maze[ny][nx] = "."
                carve_passages(nx, ny)

    carve_passages(start_x, start_y)
    maze[1][1] = "S"
    maze[height - 2][width - 2] = "E"
    return maze


def solve_maze(maze, algorithm="BFS"):
    """
    Solves the maze using the specified algorithm.

    Parameters:
        maze (list): The maze to solve.
        algorithm (str): The algorithm to use ("BFS", "DFS", "Bi-BFS", "Bi-DFS").

    Returns:
        tuple: A tuple containing the solution path and performance metrics.
    """
    height = len(maze)
    width = len(maze[0])

    # Locate start and end points
    start, end = None, None
    for y in range(height):
        for x in range(width):
            if maze[y][x] == "S":
                start = (x, y)
            elif maze[y][x] == "E":
                end = (x, y)

    if not start or not end:
        return [], {"nodes_explored": 0, "time_taken": 0, "memory_usage": 0}

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def bfs():
        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            current = queue.popleft()
            if current == end:
                path = []
                while current:
                    path.append(current)
                    current = parent[current]
                return path[::-1]

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in visited and maze[ny][nx] in {".", "E"}):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    parent[(nx, ny)] = current
        return []

    def dfs():
        stack = [start]
        visited = set()
        parent = {start: None}

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            if current == end:
                path = []
                while current:
                    path.append(current)
                    current = parent[current]
                return path[::-1]

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in visited and maze[ny][nx] in {".", "E"}):
                    stack.append((nx, ny))
                    parent[(nx, ny)] = current
        return []

    def bi_bfs():
        queue_start = deque([start])
        queue_end = deque([end])
        visited_start = {start}
        visited_end = {end}
        parent_start = {start: None}
        parent_end = {end: None}

        def reconstruct_path(meeting_point):
            path = []
            current = meeting_point
            while current:
                path.append(current)
                current = parent_start[current]
            path.reverse()
            current = parent_end[meeting_point]
            while current:
                path.append(current)
                current = parent_end[current]
            return path

        while queue_start and queue_end:
            current_start = queue_start.popleft()
            current_end = queue_end.popleft()

            if current_start in visited_end:
                return reconstruct_path(current_start)

            if current_end in visited_start:
                return reconstruct_path(current_end)

            for dx, dy in directions:
                nx, ny = current_start[0] + dx, current_start[1] + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in visited_start and maze[ny][nx] in {".", "E"}):
                    queue_start.append((nx, ny))
                    visited_start.add((nx, ny))
                    parent_start[(nx, ny)] = current_start

                nx, ny = current_end[0] + dx, current_end[1] + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in visited_end and maze[ny][nx] in {".", "S"}):
                    queue_end.append((nx, ny))
                    visited_end.add((nx, ny))
                    parent_end[(nx, ny)] = current_end

        return []

    def bi_dfs():
        stack_start = [start]
        stack_end = [end]
        visited_start = {start}
        visited_end = {end}
        parent_start = {start: None}
        parent_end = {end: None}

        def reconstruct_path(meeting_point):
            path = []
            current = meeting_point
            while current:
                path.append(current)
                current = parent_start[current]
            path.reverse()
            current = parent_end[meeting_point]
            while current:
                path.append(current)
                current = parent_end[current]
            return path

        while stack_start and stack_end:
            current_start = stack_start.pop()
            current_end = stack_end.pop()

            if current_start in visited_end:
                return reconstruct_path(current_start)

            if current_end in visited_start:
                return reconstruct_path(current_end)

            for dx, dy in directions:
                nx, ny = current_start[0] + dx, current_start[1] + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in visited_start and maze[ny][nx] in {".", "E"}):
                    stack_start.append((nx, ny))
                    visited_start.add((nx, ny))
                    parent_start[(nx, ny)] = current_start

                nx, ny = current_end[0] + dx, current_end[1] + dy
                if (0 <= nx < width and 0 <= ny < height and
                        (nx, ny) not in visited_end and maze[ny][nx] in {".", "S"}):
                    stack_end.append((nx, ny))
                    visited_end.add((nx, ny))
                    parent_end[(nx, ny)] = current_end

        return []

    tracemalloc.start()
    start_time = time.time()

    if algorithm == "BFS":
        solution = bfs()
    elif algorithm == "DFS":
        solution = dfs()
    elif algorithm == "Bi-BFS":
        solution = bi_bfs()
    elif algorithm == "Bi-DFS":
        solution = bi_dfs()
    else:
        solution = []

    end_time = time.time()
    memory_usage, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    metrics = {
        "nodes_explored": len(solution),
        "time_taken": end_time - start_time,
        "memory_usage": memory_usage / 1024
    }
    return solution, metrics


def visualize_maze(maze, solution=None):
    height = len(maze)
    width = len(maze[0])
    grid = []
    for y, row in enumerate(maze):
        grid_row = []
        for x, cell in enumerate(row):
            if cell == "#":
                grid_row.append(0)
            elif cell == "S":
                grid_row.append(2)
            elif cell == "E":
                grid_row.append(3)
            else:
                grid_row.append(1)
        grid.append(grid_row)
    if solution:
        for x, y in solution:
            if maze[y][x] not in {"S", "E"}:
                grid[y][x] = 4
    cmap = plt.cm.colors.ListedColormap(["black", "white", "green", "blue", "gray"])
    plt.imshow(grid, cmap=cmap, interpolation="nearest")
    plt.axis("off")
    plt.show()

# Command-Line Interface
def cli():
    width = int(input("Enter maze width: "))
    height = int(input("Enter maze height: "))
    algorithm = input("Choose algorithm (BFS, DFS, Bi-BFS, Bi-DFS): ")
    maze = generate_maze(width, height)
    solution, metrics = solve_maze(maze, algorithm)
    print("Performance Metrics:", metrics)
    visualize_maze(maze, solution)


if __name__ == "__main__":
    cli()

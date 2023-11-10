import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class CityGrid:
    def __init__(self, n, m, obstruction_percentage, budget):
        self.n = n
        self.m = m
        self.grid = np.zeros((n, m))
        self._place_obstructions(obstruction_percentage)
        self.towers = []  # To keep track of tower positions
        self.budget = budget
        self.tower_types = {
            'small': {'range': 1, 'cost': 15},
            'medium': {'range': 2, 'cost': 30},
            'large': {'range': 3, 'cost': 60}
        }

    def _place_obstructions(self, obstruction_percentage):
        total_blocks = self.n * self.m
        obstructed_blocks = int(total_blocks * (obstruction_percentage / 100))

        while obstructed_blocks > 0:
            x, y = random.randint(0, self.n - 1), random.randint(0, self.m - 1)
            if self.grid[x, y] == 0:
                self.grid[x, y] = -1  # -1 represents an obstruction
                obstructed_blocks -= 1

    def place_tower(self, x, y, r):
        if self.grid[x, y] == -1:
            raise ValueError("Cannot place tower on obstructed block.")

        x_start = max(0, x - r)
        x_end = min(self.n, x + r + 1)
        y_start = max(0, y - r)
        y_end = min(self.m, y + r + 1)

        for i in range(x_start, x_end):
            for j in range(y_start, y_end):
                if self.grid[i, j] != -1:  # checking if obstructions
                    self.grid[i, j] = 1  # 1 represents tower existence
        self.towers.append((x, y))

    def place_towers(self):
        uncovered_blocks = set(
            (i, j) for i in range(self.n) for j in range(self.m) if self.grid[i, j] == 0)

        while uncovered_blocks and self.budget > 0:
            best_choice = None
            best_value = 0  # coverage per unit cost

            for tower_type, properties in self.tower_types.items():
                if self.budget < properties['cost']:
                    continue  # skip if the tower type is too expensive

                r, cost = properties['range'], properties['cost']
                for i in range(self.n):
                    for j in range(self.m):
                        if self.grid[i, j] == 0:
                            coverage = len(self.calculate_coverage(i, j, r, uncovered_blocks))
                            value = coverage / cost

                            if value > best_value:
                                best_value = value
                                best_choice = (i, j, tower_type)

            if best_choice is None:
                break

            x, y, tower_type = best_choice
            self.place_tower(x, y, self.tower_types[tower_type]['range'])
            self.budget -= self.tower_types[tower_type]['cost']
            uncovered_blocks.difference_update(
                self.calculate_coverage(x, y, self.tower_types[tower_type]['range'], uncovered_blocks))

    def calculate_coverage(self, x, y, r, uncovered_blocks):
        covered_blocks = set()
        for i in range(max(0, x - r), min(self.n, x + r + 1)):
            for j in range(max(0, y - r), min(self.m, y + r + 1)):
                if (i, j) in uncovered_blocks:
                    covered_blocks.add((i, j))
        return covered_blocks

    def display_grid(self, n, m):
        """
        Display the grid using a color-coded scheme.
        """
        # color map: -1 for obstructions, 0 for free space, 1 for tower coverage
        cmap = mcolors.ListedColormap(['red', 'white', 'green'])
        bounds = [-1.5, -0.5, 0.5, 1.5]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        fig, ax = plt.subplots(figsize=(n, m))
        cax = ax.imshow(self.grid, cmap=cmap, norm=norm)
        fig.colorbar(cax, ax=ax, ticks=[-1, 0, 1], label='Block Type')
        ax.set_title("City Grid Visualization")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.grid(which='both', color='black', linestyle='-', linewidth=2)
        ax.set_xticks(range(self.m))
        ax.set_yticks(range(self.n))
        plt.show()

    def find_shortest_path(self, start, end, r):
        """
        Find the shortest path  between two towers.
        """
        # Create a graph
        graph = {tower: [] for tower in self.towers}
        for i, tower1 in enumerate(self.towers):
            for tower2 in self.towers[i + 1:]:
                if self.is_within_range(tower1, tower2, r):
                    graph[tower1].append(tower2)
                    graph[tower2].append(tower1)

        # Use breadth-first to find the shortest path
        return self.breadth_first(graph, start, end)

    def is_within_range(self, tower1, tower2, r):
        """
        Check if two towers are within range of each other.
        """
        return (abs(tower1[0] - tower2[0]) <= r and abs(
            tower1[1] - tower2[1]) <= r)

    def breadth_first(self, graph, start, end):
        """
        Breadth-First Search to find the shortest path in an unweighted graph.
        """
        visited = set()
        queue = [(start, [start])]

        while queue:
            current, path = queue.pop(0)
            if current == end:
                return path

            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # if path not found


n = 10
m = 10
obstruction_percentage = 30
budget = 150

city_grid = CityGrid(n, m, obstruction_percentage, budget)  # creating CityGrid class copy with initial values
city_grid.place_towers()  # place towers
city_grid.display_grid(n, m)  # visualize the grid
# shortest_path = city_grid.find_shortest_path(first_tower, second_tower, 2)

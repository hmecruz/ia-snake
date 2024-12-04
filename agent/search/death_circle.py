import time
import copy

from collections import deque
from typing import Optional

from consts import Direction

from ..snake import Snake
from ..grid import Grid
from ..safety import Safety

from ..utils.utils import compute_body


class Survival:
    def __init__(self, actions: Optional[list[Direction]] = None):
        self.actions = actions or [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]
        self.safety = Safety()

    def get_path(self, snake: Snake, grid: Grid, goal_depth: int) -> Optional[deque[tuple[int, int]]]:
        """
        Find the path to the best goal based on reachable tiles at depth 2.
        
        Parameters:
            snake (Snake): The snake object containing its current position, direction, and body.
            grid (Grid): The game grid object, providing access to tiles and utility methods.
            goal_depth (int): The maximum depth till the search is broken 
        Returns:
            deque[tuple[int, int]] | None: A deque representing the path to the selected goal tile, or `None` if no valid goal is found.
        """

        flood_fill_threshold = snake.size * (1.4 if snake.size >= 80 else 1.8) + 10

        path = self.compute_goal_path(snake, grid, goal_depth, flood_fill_threshold)
        if path is not None:
            return path

        print("DeathCircle: No path found")
        return None

    def compute_goal_path(
        self, 
        snake: Snake, 
        grid: Grid,
        goal_depth: int,  
        flood_fill_threshold: int, 
    ) -> Optional[deque[tuple[int, int]]]:
        """Perform BFS to explore all possible paths up to a depth of 2 and find the best goal."""
        grid_copy = copy.deepcopy(grid)
        prev_body = set(snake.body) # Save every snake position represented in the grid
        
        queue = deque([(snake.position, snake.direction, snake.body, 0)])  # (position, direction, body, depth)
        came_from = {}  # Tracks the path to reconstruct
        goals = set()  # Goals hold (goal_pos, reachable_tiles)

        visited = set([snake.position])

        while queue:
            current_pos, current_dir, current_body, current_depth = queue.popleft()

            # Stop exploring further if depth exceeds 2
            if current_depth > goal_depth:
                break

            # At depth 2, calculate reachable tiles
            if current_depth == goal_depth:
                grid_copy.update_snake_body(prev_body, current_body) # Update grid with new body
                prev_body.clear()               # Clear the old body
                prev_body.update(current_body)  # Add the new body
                reachable_cells = self.safety.flood_fill(grid, current_pos, current_dir, flood_fill_threshold)
                goals.add((current_pos, reachable_cells))
                continue

            # Explore neighbors
            neighbors = grid.get_neighbours(self.actions, current_pos, current_dir)
            for neighbor_pos, neighbor_dir in neighbors:
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    queue.append((neighbor_pos, neighbor_dir, compute_body(neighbor_pos, current_body), current_depth + 1))
                    came_from[neighbor_pos] = current_pos

        # Select the best goal based on reachable tiles
        if goals:
            best_goal = max(goals, key=lambda g: g[1])[0]  # Select the goal with the maximum reachable tiles
            return self.reconstruct_path(came_from, best_goal)

        return None

    def reconstruct_path(self, came_from: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]) -> deque[tuple[int, int]]:
        """Reconstruct the path from start to the selected goal."""
        path = deque()
        while current in came_from:
            path.appendleft(current)
            current = came_from[current]
        return path

from typing import Optional
from collections import deque

from consts import Direction

from ..snake import Snake
from ..grid import Grid

class Survival:
    def __init__(self):
        self.default_cost = 1

    def get_path(self, snake: Snake, grid: Grid) -> Optional[deque[tuple[int, int]]]:
        """Find the longest path to the snake's tail."""
        # Create a snake copy 
        # Create a grid copy
        # Find the longest path to the tail
        # When finding the longest path to the tail the snake body should be computed and registered in the grid

        print("Survival: No path found")
        return None  # No path to tail found (which shouldn't happen)
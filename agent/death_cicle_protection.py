from typing import Optional

from consts import Direction

from collections import deque
from .grid import Grid


class Death_cicle_protection:
    def __init__(self, actions: Optional[list[Direction]] = None):
        self.actions = actions or [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]

    def is_dangerous(self, grid: Grid, start_pos: tuple[int, int], current_dir: Direction) -> bool:
        visited = set()
        queue = deque([(start_pos, current_dir)])
        reachable_cells = 0

        while queue:
            # If more than 200 cells are reachable, then no death circle is assumed
            if reachable_cells >= 200:
                return True
            current_pos, current_dir = queue.popleft()
            if current_pos in visited:
                continue

            visited.add(current_pos)

            reachable_cells += 1

            # Retrieve neighbors
            neighbors = grid.get_neighbours(self.actions, current_pos, current_dir)
            for neighbor_pos, neighbor_dir in neighbors:
                if neighbor_pos not in visited:
                    queue.append((neighbor_pos, neighbor_dir))
                    
        return False
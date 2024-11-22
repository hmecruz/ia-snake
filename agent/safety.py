from typing import Optional

from consts import Direction

from collections import deque
from .grid import Grid


class Safety:
    def __init__(self, actions: Optional[list[Direction]] = None):
        self.actions = actions or [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]

    def flood_fill(self, grid: Grid, start_pos: tuple[int, int], current_dir: Direction, threshold: Optional[int] = None) -> int:
        """Perform flood-fill from the `start_pos` to find all reachable cells."""
        visited = set()
        queue = deque([(start_pos, current_dir)])
        reachable_cells = 0

        while queue:
            current_pos, current_dir = queue.popleft()
            if current_pos in visited:
                continue

            visited.add(current_pos)

            reachable_cells += 1

            # Exit early if threshold is exceeded
            if threshold is not None and reachable_cells >= threshold:
                return reachable_cells

            # Retrieve neighbors
            neighbors = grid.get_neighbours(self.actions, current_pos, current_dir)
            for neighbor_pos, neighbor_dir in neighbors:
                if neighbor_pos not in visited:
                    queue.append((neighbor_pos, neighbor_dir))
                    
        return reachable_cells
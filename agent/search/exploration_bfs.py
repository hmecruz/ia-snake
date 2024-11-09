from collections import deque
from consts import Tiles, Direction
from ..snake import Snake
from ..grid import Grid

class BFSExploration():
    def __init__(self, actions: list[Direction] = [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]):
        self.actions = actions

    def get_path(self, snake: Snake, grid: Grid) -> list[tuple[int, int]]:
        """Find the shortest path from the snake's current position to the closest Tiles.PASSAGE tile using BFS."""

        queue = deque([(snake.position, snake.direction)])  # Queue holds (position, direction)
        visited = set([snake.position])  # Visited positions
        came_from = {}  # Tracks the path

        while queue:
            current_pos, current_direction = queue.popleft()
            
            # Check if the current position is a passage tile
            if grid.get_tile(current_pos) == Tiles.PASSAGE:
                return self.reconstruct_path(came_from, current_pos)
            
            # Explore neighbors
            neighbours = self.get_neighbours(current_pos, current_direction, grid)

            for neighbour, neighbour_dir in neighbours:
                if neighbour not in visited:
                    visited.add(neighbour)
                    came_from[neighbour] = current_pos
                    queue.append((neighbour, neighbour_dir))

        print("No path to passage found")
        return None

    def get_neighbours(self, current_pos: tuple[int, int], current_direction: Direction, grid: Grid) -> list[tuple[tuple[int, int], Direction]]:
        """Return neighbors of the current position, avoiding reverse direction."""
        map_opposite_direction = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }

        neighbours = set()

        for action in self.actions:
            # Avoid moving in the reverse direction
            if action == map_opposite_direction.get(current_direction):
                continue
            
            new_position = grid.calculate_pos(current_pos, action)
            if current_pos != new_position:
                neighbours.add((new_position, action))

        return neighbours

    def reconstruct_path(self, came_from: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]) -> list[tuple[int, int]]:
        """Reconstruct the path from start to target using came_from dictionary."""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
    




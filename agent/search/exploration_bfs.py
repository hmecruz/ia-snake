from collections import deque

from consts import Tiles, Direction

from ..snake import Snake
from ..grid import Grid

class Exploration():
    def __init__(self, actions: list[Direction] = [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]):
        self.actions = actions

    def get_path(self, snake: Snake, grid: Grid, depth: bool = False, depth_limit: None | int = 0) -> deque[tuple[int, int]] | None:
        """
        Find the shortest path from the snake's current position to the nearest `Tiles.PASSAGE` tile using Breadth-First Search (BFS).

        Parameters:
            snake (Snake): The snake object containing its current position and direction.
            grid (Grid): The grid on which the snake navigates.
            depth (bool): 
                - If `False`, the search returns the first `Tiles.PASSAGE` tile found, focusing on the shortest path.
                - If `True`, the search collects all reachable `Tiles.PASSAGE` tiles within a specified depth (if `depth_limit` is set) and returns the tile with the most adjacent `Tiles.PASSAGE` tiles.
            depth_limit (int | None): 
                - Limits the search depth if set to an integer. Only goals within this depth are considered when `depth` is `True`.
                - If `None` (default), no depth limit is applied during goal search, returns the best goal from the first goal depth.

        Returns:
            deque[tuple[int, int]] | None: A list of grid positions representing the path to the chosen `Tiles.PASSAGE` tile.
                - Returns `None` if no path to any `Tiles.PASSAGE` tile is found.
        """
        queue = deque([(snake.position, snake.direction, 0)])  # Queue holds (position, direction, depth)
        visited = set([snake.position])  # Visited positions
        
        came_from = {} # Tracks the path
        
        goals = set()
        first_goal_depth = 0 # Tracks the depth of the first goal find 
        
        while queue:
            current_pos, current_dir, current_depth = queue.popleft()
            
            if goals and depth and current_depth > first_goal_depth:
                if current_depth > depth_limit:
                    best_goal = self.select_best_goal(goals, grid, snake.range)
                    return self.reconstruct_path(came_from, best_goal)

            # Check if the current position is a passage tile
            if grid.get_tile(current_pos) == Tiles.PASSAGE:
                if depth: 
                    if not goals: 
                        first_goal_depth = current_depth
                    goals.add((current_pos)) 
                else: 
                    return self.reconstruct_path(came_from, current_pos)
            
            # Explore neighbors
            neighbours = grid.get_neighbours(self.actions, current_pos, current_dir, snake.eat_super_food)

            for neighbour_pos, neighbour_dir in neighbours:
                if neighbour_pos not in visited:
                    visited.add(neighbour_pos)
                    came_from[neighbour_pos] = current_pos
                    queue.append((neighbour_pos, neighbour_dir, current_depth+1))

        print("No path to passage found")
        return None
    

    def select_best_goal(self, goals: set[tuple[int, int]], grid: Grid, size: int) -> tuple[int, int]:
        """Select the goal with the maximum number of Tiles.PASSAGE in zone."""
        max_passages = -1
        best_goal = None
        
        for goal in goals:
            zone = grid.get_zone(goal, size)
            passages = sum(1 for row in zone.values() for tile in row.values() if tile == Tiles.PASSAGE)
            
            if passages > max_passages:
                max_passages = passages
                best_goal = goal
        
        return best_goal

    def reconstruct_path(self, came_from: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]) -> deque[tuple[int, int]]:
        """Reconstruct the path from start to target using came_from dictionary."""
        path = deque()  # Use deque for efficient appending to the left
        while current in came_from:
            path.appendleft(current)  # Append to the left, so no need to reverse later
            current = came_from[current]
        return path  # Return deque directly
    

    def possible_actions(self, current_pos: tuple[int, int], current_dir: Direction, grid: Grid) -> set[Direction]:
        """Return neighbors of the current position, avoiding reverse direction."""
        map_opposite_direction = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }

        """
        possible_actions = {
            action for action in self.actions
            if action != opposite_direction.get(current_dir)
            and grid.calculate_pos(current_pos, action) != current_pos
        }
        """
        possible_actions = set()

        for action in self.actions:
            # Avoid moving in the reverse direction
            if action == map_opposite_direction.get(current_dir):
                continue
            
            new_position = grid.calculate_pos(current_pos, action)
            if current_pos != new_position:
                possible_actions.add(action)

        return possible_actions
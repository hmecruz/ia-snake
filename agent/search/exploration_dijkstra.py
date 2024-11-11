import heapq

from collections import deque

from consts import Tiles, Direction

from ..snake import Snake
from ..grid import Grid

class Exploration():
    def __init__(
        self, 
        actions: list[Direction] = [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH], 
        tile_costs: dict[Tiles, int] | None = None
    ):
        self.actions = actions
        self.tile_costs = tile_costs if tile_costs is not None else {
            Tiles.PASSAGE: 1,
            Tiles.STONE: 5,    
            Tiles.VISITED: 4
        }
        self.default_cost = 1

    def get_path(self, snake: Snake, grid: Grid, depth: bool = False, depth_limit: None | int = 0) -> deque[tuple[int, int]] | None:
        """
        Find the least costing path from the snake's current position to the nearest `Tiles.PASSAGE` tile using Dijkstra's algorithm.

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
        
        # Super Food Cost
        self.tile_costs[Tiles.SUPER] = 0 if snake.eat_super_food else 15
        
        open_list = []
        heapq.heappush(open_list, (0, snake.position, snake.direction, 0)) # Queue holds (cost, position, direction, depth)
        visited = set([snake.position])  # Visited positions
        
        came_from = {}  # Tracks the path
        costs = {snake.position: 0}  # Cost to reach each position
        
        goals = set()
        first_goal_depth = 0  # Tracks the depth of the first goal found
        
        while open_list:
            current_cost, current_pos, current_dir, current_depth = heapq.heappop(open_list)
            
            # Stop if depth limit exceeded in depth mode
            if goals and depth and current_depth > first_goal_depth:
                if current_depth > depth_limit:
                    best_goal = self.select_best_goal(goals, grid, snake.range)
                    return self.reconstruct_path(came_from, best_goal)

            # Check if the current position is a passage tile
            if grid.get_tile(current_pos) == Tiles.PASSAGE:
                if depth:
                    if not goals:
                        first_goal_depth = current_depth
                    goals.add(current_pos)
                else:
                    return self.reconstruct_path(came_from, current_pos)

            # Explore neighbors
            neighbours = grid.get_neighbours(self.actions, current_pos, current_dir, snake.eat_super_food)

            for neighbor_pos, neighbor_dir in neighbours:
                tile_cost = self.tile_costs.get(grid.get_tile(neighbor_pos), self.default_cost) # Tile weight for neighbor
                new_cost = current_cost + tile_cost 

                if neighbor_pos not in visited or new_cost < costs.get(neighbor_pos, float('inf')): # If new neighbour or neighbour with less cost
                    visited.add(neighbor_pos)
                    costs[neighbor_pos] = new_cost
                    heapq.heappush(open_list, (new_cost, neighbor_pos, neighbor_dir, current_depth + 1))
                    came_from[neighbor_pos] = current_pos

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
        path = deque()
        while current in came_from:
            path.appendleft(current)
            current = came_from[current]
        return path

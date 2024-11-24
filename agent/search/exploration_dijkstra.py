import copy
import heapq

from typing import Union, Optional
from collections import deque

from consts import Tiles, Direction

from ..snake import Snake
from ..grid import Grid
from ..safety import Safety

from ..utils.utils import compute_body

class Exploration:
    def __init__(
        self, 
        actions: Optional[list[Direction]] = None, 
        tile_costs: Optional[dict[Tiles, int]] = None,
    ):
        self.actions = actions or [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]

        self.tile_costs = tile_costs or {
            Tiles.VISITED: 1,
            Tiles.STONE: 5
        }
        self.default_cost = 1
        self.safety = Safety()

        
    def get_path(self, snake: Snake, grid: Grid, depth: bool = False, flood_fill: bool = True) -> Optional[deque[tuple[int, int]]]: 
        """
        Find the least costing path from the snake's current position to the best goal tile, considering `Tiles.VISITED` tiles with an age of at least 2. Uses a variant of Dijkstra's algorithm to find paths in a grid.

        Parameters:
            snake (Snake): The snake object containing its current position, direction, and state (e.g., if it has eaten super food).
            grid (Grid): The grid on which the snake navigates, used to retrieve tile information and neighbours.
            depth (bool): 
                - If `False`, the search will return the first valid `Tiles.VISITED` tile found, based on cost.
                - If `True`, the search collects all reachable valid `Tiles.VISITED` tiles and selects the one with the lowest combined cost (cost of reaching the goal minus the sum of the ages of surrounding `Tiles.VISITED` tiles).
            depth_limit (int | None): 
                - If `depth` is `True`, this limits how far the search will explore. If not specified (default `None`), it will search until all goals are found within the first goal depth and select the best goal.
            flood_fill (bool):
                - If 'True' the search will only consider a goal if the agent is able to access at least 'flood_fill_threshold' tiles
                - If 'False' the search will not consider the tiles the agent is able to access after it reaches the chosen goal 
        Returns:
            deque[tuple[int, int]] | None: A deque representing the path to the selected goal tile, or `None` if no path to any valid goal is found.
                - The path will contain grid positions leading to the best `Tiles.VISITED` tile.
        """
        
        # Super Food Cost
        self.tile_costs[Tiles.SUPER] = 0 if snake.eat_super_food else 25
        
        # Flood Fill threshold
        if flood_fill:
            flood_fill_threshold = snake.size * (1.3 if snake.size >= 80 else 1.8)
        else:
            flood_fill_threshold = None
        print(f"Flood Fill Threshold: {flood_fill_threshold}")

        path = self.compute_goal_path(snake, grid, depth, flood_fill_threshold)
        if path is not None:
            return path

        print(f"Exploration: No path found")
        return None


    def compute_goal_path(self, snake: Snake, grid: Grid, depth: bool, flood_fill_threshold: Optional[int]) -> Optional[deque[tuple[int, int]]]:
        grid_copy = copy.deepcopy(grid)
        prev_body = set(snake.body) # Save every snake position represented in the grid

        open_list = []
        heapq.heappush(open_list, (0, snake.position, snake.direction, snake.body, 0)) # Queue holds (cost, position, direction, body, depth)
        visited = set([snake.position])  # Visited positions
        
        came_from = {}  # Tracks the path
        costs = {snake.position: 0}  # Cost to reach each position
        
        goals = set() # Goals hold (goal_pos, cost)
        first_goal_depth = 0  # Tracks the depth of the first goal found
        
        while open_list:
            current_cost, current_pos, current_dir, current_body, current_depth = heapq.heappop(open_list)
            
            # Early exit if the current node depth exceeds the first goal depth
            if goals and depth and (current_depth > first_goal_depth + 1 or len(goals) >= 5):
                best_goal = self.select_best_goal(goals, grid, snake.range)
                return self.reconstruct_path(came_from, best_goal)
                
            # Goal Test
            tile_value = grid.get_tile(current_pos)
            if self.is_valid_goal(grid_copy, tile_value, current_pos, current_dir, prev_body, current_body, flood_fill_threshold):
                if depth:
                    if not goals:
                        first_goal_depth = current_depth
                    goals.add((current_pos, current_cost))
                else:
                    return self.reconstruct_path(came_from, current_pos)

            # Explore neighbours
            neighbours = grid.get_neighbours(self.actions, current_pos, current_dir)

            for neighbour_pos, neighbour_dir in neighbours:
                tile_value = grid.get_tile(neighbour_pos)
                neighbour_cost = self.get_tile_cost(tile_value)
                new_cost = current_cost + neighbour_cost

                if neighbour_pos not in visited or new_cost < costs.get(neighbour_pos, float('inf')): # If cheaper path
                    visited.add(neighbour_pos)
                    costs[neighbour_pos] = new_cost
                    heapq.heappush(open_list, (new_cost, neighbour_pos, neighbour_dir, compute_body(neighbour_pos, current_body), current_depth + 1))
                    came_from[neighbour_pos] = current_pos

        if goals and depth:
            best_goal = self.select_best_goal(goals, grid, snake.range)
            return self.reconstruct_path(came_from, best_goal)

        return None
    
    
    def is_valid_goal(
            self, 
            grid: Grid, 
            tile_value: Union[Tiles, tuple[Tiles, int]], 
            current_pos: tuple[int, int], 
            current_dir: Direction, 
            prev_body: set[tuple[int, int]], 
            current_body: list[tuple[int, int]], 
            flood_fill_threshold: Optional[int]) -> bool:
        """Check if the tile is a valid goal (Tiles.VISITED with age >= 2)."""
        """Check if the goal when using flood fill suprasses X amount of available cells to visit --> Avoids Box in situations"""
        if isinstance(tile_value, tuple) and tile_value[0] == Tiles.VISITED and tile_value[1] >= 2:
            if flood_fill_threshold is None: return True
            grid.update_snake_body(prev_body, current_body) # Update grid with new body
            prev_body.clear()               # Clear the old body
            prev_body.update(current_body)  # Add the new body
            reachable_cells = self.safety.flood_fill(grid, current_pos, current_dir, flood_fill_threshold)
            return reachable_cells >= flood_fill_threshold
        return False

    def get_tile_cost(self, tile_value: Tiles | tuple[Tiles, int]) -> int :
        """Return the cost associated with a tile."""
        if isinstance(tile_value, tuple) and tile_value[0] == Tiles.VISITED:
            return self.tile_costs[Tiles.VISITED]
        return self.tile_costs.get(tile_value, self.default_cost)

    def select_best_goal(self, goals: set[tuple[int, int]], grid: Grid, size: int) -> tuple[int, int]:
        """Select the goal with the maximum number of Tiles.PASSAGE in zone."""
        best_goal = None
        min_goal_value = float('inf')
        
        for goal_pos, goal_cost in goals:
            zone = grid.get_zone(goal_pos, size)
            sum_ages = sum(
                tile[1] for row in zone.values() for tile in row.values() 
                if isinstance(tile, tuple) and tile[0] == Tiles.VISITED
            )
            goal_value = goal_cost - sum_ages  # Lower value corresponds to a better exploration
        
            if goal_value < min_goal_value:
                min_goal_value = goal_value
                best_goal = goal_pos

        return best_goal

    def reconstruct_path(self, came_from: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]) -> deque[tuple[int, int]]:
        """Reconstruct the path from start to target using came_from dictionary."""
        path = deque()
        while current in came_from:
            path.appendleft(current)
            current = came_from[current]
        return path

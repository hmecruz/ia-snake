import time
import copy
import heapq

from typing import Optional, Union
from collections import deque

from consts import Direction, Tiles

from ..snake import Snake
from ..grid import Grid
from ..safety import Safety

from ..utils.utils import compute_body, get_start_time
class Eating:
    def __init__(
        self, 
        actions: Optional[list[Direction]] = None, 
    ):
        self.actions = actions or [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]

        self.goal_tile_costs = {
            "food": {
                Tiles.STONE: 1,
                Tiles.VISITED: 1,
                Tiles.ENEMY_SUPPOSITION: 100,
                Tiles.FOOD: 0,
            },
            "super_food": {
                Tiles.STONE: 10,
                Tiles.VISITED: 7, # minus age --> Tile.VISITED [1, 7] cost range --> Useful for longer paths
                Tiles.ENEMY_SUPPOSITION: 100,
                Tiles.FOOD: 0,
                Tiles.SUPER: 0,
            },
        }

        self.default_cost = 5
        self.safety = Safety()


    def get_path(self, snake: Snake, grid: Grid) -> Optional[deque[tuple[int, int]]]:
        """Find the lowest cost path using A* from the snake's current position to the closest reachable food"""
                
        # Super food cost
        self.goal_tile_costs["food"][Tiles.SUPER] = 0 if snake.eat_super_food else 25

        # Flood Fill threshold
        flood_fill_threshold = snake.size * (1.4 if snake.size >= 80 else 1.8)

        goals_queue = self.sort_goals(snake.position, grid.food, grid.super_food, grid.size, grid.traverse, snake.eat_super_food)
        if not goals_queue and snake.eat_super_food: 
            raise ValueError(f"No food found in grid.food: {grid.food}. No food found in grid.super_food: {grid.super_food}")
        elif not goals_queue: 
            raise ValueError(f"No food found in grid.food: {grid.food}.")
            
        for goal in goals_queue:
            goal_type = "food" if goal in grid.food else "super_food"
            path = self.compute_goal_path(snake, grid, goal, goal_type, flood_fill_threshold)
            if path is not None:
                return path

        print(f"Eating: No path found")
        return None


    def compute_goal_path(self, snake: Snake, grid: Grid, goal: tuple[int, int], goal_type: str, flood_fill_threshold: int) -> Optional[deque[tuple[int, int]]]:
        grid_copy = copy.deepcopy(grid)
        prev_body = set(snake.body) # Save every snake position represented in the grid
        
        open_list = []
        heapq.heappush(open_list, (0, snake.position, snake.direction, snake.body))  # (f_cost, position, direction, body)
        visited = set() # Visited positions

        came_from = {}
        g_costs = {snake.position: 0} # Stores the cost from start to each position
        f_costs = {snake.position: self.heuristic(snake.position, goal, grid.size, grid.traverse)} # g_score + heuristic

        while open_list:
            if (time.time() - get_start_time()) * 1000 > 85: 
                print("Exit due to computational time")
                break # Exit cycle if the computation time exceeds 85ms 

            current_cost, current_pos, current_direction, current_body = heapq.heappop(open_list) # Pop node with the lowest f_score from heap
            
            if current_pos in visited:
                continue # Position has already been visited
                
            # Check if the current position is a passage tile 
            if self.is_valid_goal(grid_copy, current_pos, current_direction, goal, goal_type, prev_body, current_body, flood_fill_threshold):
                return self.reconstruct_path(came_from, current_pos)
            
            visited.add(current_pos) # Add current position to visited 
            
            # Explore neighbours
            neighbours = grid.get_neighbours(self.actions, current_pos, current_direction)

            for neighbour_pos, neighbour_dir in neighbours:
                tile_value = grid.get_tile(neighbour_pos)
                tile_cost = self.get_tile_cost(tile_value, goal_type)  # Get the correct cost based on the tile type and age
                new_cost = current_cost + tile_cost
                
                # Update g_score, f_score, and add to open list if it has not been processed or has a better score
                if neighbour_pos not in g_costs or new_cost < g_costs.get(neighbour_pos, float('inf')):
                    came_from[neighbour_pos] = current_pos
                    g_costs[neighbour_pos] = new_cost
                    f_cost = new_cost + self.heuristic(neighbour_pos, goal, grid.size, grid.traverse)
                    f_costs[neighbour_pos] = f_cost
                    heapq.heappush(open_list, (f_cost, neighbour_pos, neighbour_dir, compute_body(neighbour_pos, current_body)))

        return None # No path to goal found

    
    def is_valid_goal(
            self, 
            grid: Grid, 
            current_pos: tuple[int, int], 
            current_dir: Direction, 
            goal: tuple[int, int], 
            goal_type: str,
            prev_body: set[tuple[int, int]], 
            current_body: list[tuple[int, int]],
            flood_fill_threshold: int) -> bool:
        """Check if the goal when using flood fill suprasses X amount of available cells to visit --> Avoids Box in situations"""
        if current_pos == goal:
            grid.update_snake_body(prev_body, current_body) # Update grid with new body
            prev_body.clear()               # Clear the old body
            prev_body.update(current_body)  # Add the new body

            previous_traverse = grid.traverse  # Save the current traverse state 
            if goal_type == "super_food":
                grid.traverse = False  # Update grid traversal to False since eating a super food can change the traverse state of the grid
            
            reachable_cells = self.safety.flood_fill(grid, current_pos, current_dir, flood_fill_threshold)
            
            if goal_type == "super_food":
                grid.traverse = previous_traverse  # Restore grid traversal state

            return reachable_cells >= flood_fill_threshold

    def reconstruct_path(self, came_from: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]) -> deque[tuple[int, int]]:
        """Reconstruct the path from start to target using came_from dictionary."""
        path = deque()  # Use deque for efficient appending to the left
        while current in came_from:
            path.appendleft(current)  # Append to the left, so no need to reverse later
            current = came_from[current]
        return path  # Return deque directly
    
    def sort_goals(
        self,
        cur_pos: tuple[int, int],
        food_positions: set[tuple[int, int]],
        super_food_positions: set[tuple[int, int]],
        grid_size: tuple[int, int],
        grid_traverse: bool,
        eat_super_food: bool
    ) -> Optional[list[tuple[int, int]]]:
        """Find the closest foods positions to the start position, using a min-heap to optimize selection."""
        
        if not food_positions and not (eat_super_food and super_food_positions):
            return None  # No food available to target

        target_positions = food_positions | super_food_positions if eat_super_food else food_positions

        # Priority heap for goals
        heap = [
            (self.heuristic(cur_pos, pos, grid_size, grid_traverse), pos)
            for pos in target_positions
        ]
        heapq.heapify(heap)  
        
        # Extract the closest 3 goals (if there are that many) from the heap
        closest_goals = []
        for _ in range(min(3, len(heap))):
            closest_goals.append(heapq.heappop(heap)[1])  # Pop and collect the positions

        return closest_goals

    def heuristic(self, pos: tuple[int, int], goal: tuple[int, int], grid_size: tuple[int, int], grid_traverse: bool) -> int:
        """Heuristic function that calculates Manhattan distance with wrap-around consideration."""
        pos_x, pos_y = pos
        goal_x, goal_y = goal
        grid_width, grid_height = grid_size

        # Calculate the direct distance along each axis
        dx = abs(pos_x - goal_x)
        dy = abs(pos_y - goal_y)

        if not grid_traverse:
            return dx + dy

        # Calculate wrap-around distances along each axis
        wrap_dx = grid_width - dx
        wrap_dy = grid_height - dy

        # Use the shorter distance for each axis
        shortest_dx = min(dx, wrap_dx)
        shortest_dy = min(dy, wrap_dy)

        # Manhattan distance considering wrap-around
        return shortest_dx + shortest_dy
    
    def get_tile_cost(self, tile_value: Union[Tiles, tuple[Tiles, float, int]], goal_type: str) -> int:
        """Return the cost associated with a tile."""
        costs = self.goal_tile_costs[goal_type]

        if isinstance(tile_value, tuple) and tile_value[0] == Tiles.VISITED:
            base_cost = costs[Tiles.VISITED]
            if goal_type == "super_food":
                return base_cost - max(0, min(6, tile_value[1] / 20))
            return base_cost

        return costs.get(tile_value, self.default_cost)

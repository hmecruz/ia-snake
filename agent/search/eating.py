import heapq

from collections import deque

from consts import Direction, Tiles

from ..snake import Snake
from ..grid import Grid

class Eating():
    def __init__(
        self, 
        actions: list[Direction] = [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH],
        tile_costs: dict[Tiles, int] | None = None
    ):
        self.actions = actions
        self.tile_costs = tile_costs if tile_costs is not None else {
            Tiles.STONE: 6,    
            Tiles.VISITED: 5,
            Tiles.FOOD: 0
        }
        self.default_cost = 1

    def get_path(self, snake: Snake, grid: Grid) -> deque[tuple[int, int]]:
        """Find the lowest cost path using A* from the snake's current position to the closest reachable food"""
        
        # Super Food Cost
        self.tile_costs[Tiles.SUPER] = 2 if snake.eat_super_food else 15

        goal, eat_super_food = self.find_goal(snake.position, grid.food, grid.super_food, grid.size, grid.traverse, snake.eat_super_food)
        if not goal and eat_super_food: 
            raise ValueError(f"No food found in {grid.food}. No food found in {grid.super_food}")
        elif not goal: 
            raise ValueError(f"No food found in {grid.food}.")
            
        open_list = []
        heapq.heappush(open_list, (0, snake.position, snake.direction))  # (f_cost, position, direction)
        visited = set() # Visited positions

        came_from = {}
        g_costs = {snake.position: 0} # Stores the cost from start to each position
        f_costs = {snake.position: self.heuristic(snake.position, goal, grid.size, grid.traverse)} # g_score + heuristic

        while open_list:
            _, current_pos, current_direction = heapq.heappop(open_list) # Pop node with the lowest f_score from heap
            
            if current_pos in visited:
                continue # Position has already been visited
                
            # Check if the current position is a passage tile 
            if current_pos == goal:
                return self.reconstruct_path(came_from, current_pos)
            
            visited.add(current_pos) # Add current position to visited 

            # Explore neighbours
            neighbours = grid.get_neighbours(self.actions, current_pos, current_direction)

            for neighbour_pos, neighbour_dir in neighbours:
                tile_value = grid.get_tile(neighbour_pos)
                tile_cost = self.get_tile_cost(tile_value)  # Get the correct cost based on the tile type and age
                tentative_g_cost = g_costs[current_pos] + tile_cost
                
                # Update g_score, f_score, and add to open list if it has not been processed or has a better score
                if neighbour_pos not in g_costs or tentative_g_cost < g_costs[neighbour_pos]:
                    came_from[neighbour_pos] = current_pos
                    g_costs[neighbour_pos] = tentative_g_cost
                    f_cost = tentative_g_cost + self.heuristic(neighbour_pos, goal, grid.size, grid.traverse)
                    f_costs[neighbour_pos] = f_cost
                    heapq.heappush(open_list, (f_cost, neighbour_pos, neighbour_dir))

        print("No path found")
        return None
    

    def reconstruct_path(self, came_from: dict[tuple[int, int], tuple[int, int]], current: tuple[int, int]) -> deque[tuple[int, int]]:
        """Reconstruct the path from start to target using came_from dictionary."""
        path = deque()  # Use deque for efficient appending to the left
        while current in came_from:
            path.appendleft(current)  # Append to the left, so no need to reverse later
            current = came_from[current]
        return path  # Return deque directly

    
    def find_goal(self, 
            cur_pos              : tuple[int, int], 
            food_positions       : set[tuple[int, int]], 
            super_food_positions : set[tuple[int, int]],
            grid_size            : tuple[int, int],
            grid_traverse        : bool,
            eat_super_food       : bool
            ) -> tuple[int, int] | None:
        """Find the closest food position to the start position"""
        
        if not food_positions and not (eat_super_food and super_food_positions):
            return None, eat_super_food  # No food available to target

        target_positions = food_positions | super_food_positions if eat_super_food else food_positions

        # Return the closest position to cur_pos from the target positions
        return min(target_positions, key=lambda pos: self.heuristic(cur_pos, pos, grid_size, grid_traverse)), eat_super_food

    
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
    
    def get_tile_cost(self, tile_value: Tiles | tuple[Tiles, int]) -> int:
        """Return the cost associated with a tile."""
        if isinstance(tile_value, tuple) and tile_value[0] == Tiles.VISITED:
            return self.tile_costs[Tiles.VISITED]  # Use the default cost for VISITED tiles (can adjust based on age if needed)
        return self.tile_costs.get(tile_value, self.default_cost)

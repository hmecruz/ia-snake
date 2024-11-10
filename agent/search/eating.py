import heapq

from consts import Direction

from ..snake import Snake
from ..grid import Grid

class Eating():
    def __init__(self, actions: list[Direction] = [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]):
        self.actions = actions

    def get_path(self, snake: Snake, grid: Grid) -> list[tuple[int, int]]:
        """Find the shortest path from the snake's current position to the closest reachable food"""
        
        goal = self.find_goal(snake.position, grid.food, grid.super_food, grid.size, snake.eat_super_food)
        if not goal: raise ValueError(f"No food found in {grid.food}")
            
        open_list = []
        heapq.heappush(open_list, (0, snake.position, snake.direction))  # (f_cost, position, direction)
        closed_list = set() # Visited positions

        came_from = {}
        g_costs = {snake.position: 0} # Actual cost from the start cell to each cell
        f_costs = {snake.position: self.heuristic(snake.position, goal, grid.size)} # g_score + heuristic

        while open_list:
            _, current_pos, current_direction = heapq.heappop(open_list) # Pop node with the lowest f_score from heap
            
            if current_pos in closed_list:
                continue # Position has already been visited
                
            # Check if the current position is a passage tile 
            if current_pos == goal:
                return self.reconstruct_path(came_from, current_pos)
            
            closed_list.add(current_pos) # Add current position to visited 

            # Explore neighbours
            neighbours = grid.get_neighbours(self.actions, current_pos, current_direction)

            for neighbour, neighbour_dir in neighbours:
                tentative_g_cost = g_costs[current_pos] + 1
                
                # Update g_score, f_score, and add to open list if it has not been processed or has a better score
                if neighbour not in g_costs or tentative_g_cost < g_costs[neighbour]:
                    came_from[neighbour] = current_pos
                    g_costs[neighbour] = tentative_g_cost
                    f_cost = tentative_g_cost + self.heuristic(neighbour, goal, grid.size)
                    f_costs[neighbour] = f_cost
                    heapq.heappush(open_list, (f_cost, neighbour, neighbour_dir))

        print("No path found")
        return None
    

    def reconstruct_path(self, came_from: dict[tuple[int, int]], current: tuple[int, int]) -> list[tuple[int, int]]:
        # Reconstruct the path from start to target
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
    

    def find_goal(self, 
            cur_pos              : tuple[int, int], 
            food_positions       : set[tuple[int, int]], 
            super_food_positions : set[tuple[int, int]],
            grid_size            : tuple[int, int],
            eat_super_food       : bool
            ) -> tuple[int, int] | None:
        """Find the closest food position to the start position"""
        
        if not food_positions and not (eat_super_food and super_food_positions):
            return None  # No food available to target

        target_positions = food_positions | super_food_positions if eat_super_food else food_positions

        # Return the closest position to cur_pos from the target positions
        return min(target_positions, key=lambda pos: self.heuristic(cur_pos, pos, grid_size))

    
    def heuristic(self, pos: tuple[int, int], goal: tuple[int, int], grid_size: tuple[int, int]) -> int:
        """Heuristic function that calculates Manhattan distance with wrap-around consideration."""
        pos_x, pos_y = pos
        goal_x, goal_y = goal
        grid_width, grid_height = grid_size

        # Calculate the direct distance along each axis
        dx = abs(pos_x - goal_x)
        dy = abs(pos_y - goal_y)

        # Calculate wrap-around distances along each axis
        wrap_dx = grid_width - dx
        wrap_dy = grid_height - dy

        # Use the shorter distance for each axis
        shortest_dx = min(dx, wrap_dx)
        shortest_dy = min(dy, wrap_dy)

        # Manhattan distance considering wrap-around
        return shortest_dx + shortest_dy

    #def heuristic(self, pos: tuple[int, int], goal: tuple[int, int], grid_size: tuple[int, int]) -> int:
    #    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    

    
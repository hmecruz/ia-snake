import heapq

from consts import Tiles, Direction
from ..snake import Snake
from ..grid import Grid

class AStarEating():
    def __init__(self, actions: list[Direction] = [Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH]):
        self.actions = actions

    def get_path(self, snake: Snake, grid: Grid) -> list[tuple[int, int]]:
        """Find the shortest path from the snake's current position to the first reachable Tiles.PASSAGE tile."""

        open_list = []
        heapq.heappush(open_list, (0, snake.position, snake.direction))  # (f_cost, position, direction)        closed_list = set() # Visited positions
        closed_list = set() # Visited positions


        came_from = {}
        g_costs = {snake.position: 0} # Actual cost from the start cell to each cell
        f_costs = {snake.position: self.heuristic(snake.position, grid)} # g_score + heuristic

        while open_list:
            _, current_pos, current_direction = heapq.heappop(open_list) # Pop node with the lowest f_score from heap
            
            if current_pos in closed_list:
                continue # Position has already been visited
                
            # Check if the current position is a passage tile 
            if grid.get_tile(current_pos) == Tiles.PASSAGE:
                return self.reconstruct_path(came_from, current_pos)
            
            closed_list.add(current_pos) # Add current position to visited 

            # Explore neighbours
            neighbours = self.get_neighbours(current_pos, current_direction, grid)

            for neighbour, neighbour_dir in neighbours:
                tentative_g_cost = g_costs[current_pos] + 1
                
                # Update g_score, f_score, and add to open list if it has not been processed or has a better score
                if neighbour not in g_costs or tentative_g_cost < g_costs[neighbour]:
                    came_from[neighbour] = current_pos
                    g_costs[neighbour] = tentative_g_cost
                    f_cost = tentative_g_cost + self.heuristic(neighbour, grid)
                    f_costs[neighbour] = f_cost
                    heapq.heappush(open_list, (f_cost, neighbour, neighbour_dir))

        print("No path found")
        return None
    

    def get_neighbours(self, current_pos: tuple[int, int], current_direction: Direction, grid: Grid) -> set[tuple[tuple[int, int], Direction]]:
        map_opposite_direction = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }

        neighbours = set()

        for action in self.actions:
            if action == map_opposite_direction.get(current_direction): # Snake can't move to the opposite direction of its current direction
                continue

            new_position = grid.calc_pos(current_pos, action, grid.traverse)
            if current_pos != new_position:
                neighbours.add((new_position, action))
                
        return neighbours

    def reconstruct_path(self, came_from: dict[tuple[int, int]], current: tuple[int, int]) -> list[tuple[int, int]]:
        # Reconstruct the path from start to target
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    
    def heuristic(self, position: tuple[int, int], grid: Grid) -> int:
        x, y = position
        return min(
            abs(x - i) + abs(y - j)
            for i in range(grid.hor_tiles)
            for j in range(grid.ver_tiles)
            if grid.get_tile((i, j)) == Tiles.PASSAGE
        )
    

    
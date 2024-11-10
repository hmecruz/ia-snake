import math
import copy 

from consts import Tiles, Direction
from agent.snake import Snake

class Grid:
    def __init__(self, size: tuple[int, int], grid: list[list]):
        self._size = size
        self.grid = grid
        self._stones = self._set_stones()
        self._food = set() 
        self._super_food = set()
        self._traverse = None
        
        self._ate_food = False
        self._ate_super_food = False
        
        self._visited_tiles_clear_counter = 0
        self._visited_tiles_clear_limit = None # Number of foods to eat before clearing visited tiles


    def __repr__(self):
        return f"Grid(size={self.size}, stones={len(self.stones)} stones, food={len(self.food)} items, super_food={len(self.super_food)} items)"

    def __str__(self):
        return f"Grid - Size: {self.size}, Stones: {len(self.stones)}, Food: {len(self.food)}, Super Food: {len(self.super_food)}, Traverse: {self.traverse}"

    def __deepcopy__(self, memo):
        copied = Grid(self._size, copy.deepcopy(self.grid, memo))
        copied._stones = copy.deepcopy(self._stones, memo)
        copied._food = copy.deepcopy(self._food, memo)
        copied._super_food = copy.deepcopy(self._super_food, memo)
        copied._traverse = self._traverse
        return copied
    
    @property
    def hor_tiles(self) -> int:
        return self._size[0]

    @property
    def ver_tiles(self) -> int:
        return self._size[1]

    @property
    def size(self) -> tuple[int, int]:
        return self._size
    
    @property
    def stones(self) -> set[tuple[int, int]]:
        return self._stones

    @property
    def food(self) -> set[tuple[int, int]]:
        return self._food
    
    @property
    def super_food(self) -> set[tuple[int, int]]:
        return self._super_food

    @property
    def traverse(self) -> bool:
        return self._traverse
    
    @traverse.setter
    def traverse(self, traverse: bool):
        if not isinstance(traverse, bool):
            raise ValueError(f"Invalid value for traverse: {traverse}. Expected a boolean.")
        self._traverse = traverse

    @property
    def ate_food(self) -> bool:
        return self._ate_food
    
    @ate_food.setter
    def ate_food(self, ate_food: bool):
        if not isinstance(ate_food, bool):
            raise ValueError(f"Invalid value for ate_food: {ate_food}. Expected a boolean.")
        self._ate_food = ate_food

    @property
    def ate_super_food(self) -> bool:
        return self._ate_super_food

    @ate_super_food.setter
    def ate_super_food(self, ate_super_food: bool):
        if not isinstance(ate_super_food, bool):
            raise ValueError(f"Invalid value for ate_super_food: {ate_super_food}. Expected a boolean.")
        self._ate_super_food = ate_super_food

    @property
    def visited_tiles_clear_counter(self) -> int:
        return self._visited_tiles_clear_counter

    @visited_tiles_clear_counter.setter
    def visited_tiles_clear_counter(self, counter: int):
        if not isinstance(counter, int) or counter < 0:
            raise ValueError(f"Invalid value for visited_tiles_clear_counter: {counter}. Expected a non-negative integer.")
        self._visited_tiles_clear_counter = counter

    @property
    def visited_tiles_clear_limit(self) -> int:
        return self._visited_tiles_clear_limit

    @visited_tiles_clear_limit.setter
    def visited_tiles_clear_limit(self, limit: int):
        if not isinstance(limit, int) or limit < 1 or limit > 4:
            raise ValueError(f"Invalid value for visited_tiles_clear_limit: {limit}. Expected a integer between 1 and 4 inclusive.")
        self._visited_tiles_clear_limit = limit
    
        
    def _set_stones(self) -> set[tuple[int, int]]: 
        """Initialize the positions of stones on the grid."""
        stones = set()
        for x in range(self.hor_tiles):
            for y in range(self.ver_tiles):
                if self.grid[x][y] == Tiles.STONE:
                    stones.add((x, y)) # Store stone positions
        return stones


    def get_tile(self, pos: tuple[int, int]) -> Tiles:
        x, y = pos
        return self.grid[x][y]
    

    def update(self, pos: tuple[int, int], body: list[list[int]], size: int, prev_body: list[list[int]], sight: dict[int, dict[int, Tiles]], traverse: bool):    
        self.traverse = traverse
        self._update_visited_tiles_clear_limit(size) # Must be called first
        eat_food, eat_super_food = self._update_food(pos, sight)
        self._update_visited_tiles(sight) 
        self._update_snake_body(pos, body, prev_body, eat_food, eat_super_food)

        
    def _update_visited_tiles_clear_limit(self, size):
        if 30 <= size < 60:
            self.visited_tiles_clear_limit = 3
        elif size >= 60:
            self.visited_tiles_clear_limit = 2
        else: 
            self.visited_tiles_clear_limit = 4

    
    def _update_food(self, pos: tuple[int, int], sight: dict[int, dict[int, Tiles]]) -> bool:
        """Update the food and super food positions on the grid."""
        # sight': {6: {17: 0}, 7: {15: 1, 16: 0, 17: 0, 18: 0, 19: 0}
        for x, y_tile in sight.items():
            for y, tile in y_tile.items():
                # Mark food and super_food 
                if tile == Tiles.FOOD:
                    self._food.add((x, y))
                    self.grid[x][y] = Tiles.FOOD  
                elif tile == Tiles.SUPER:
                    self._super_food.add((x, y)) 
                    self.grid[x][y] = Tiles.SUPER
        
        # Eat food and super_food
        if pos in self.food:
            self.food.discard(pos)
            self.visited_tiles_clear_counter += 1  
            if self.visited_tiles_clear_counter % self.visited_tiles_clear_limit == 0:
                self.clear_visited_tiles() # Clear all visited cells
            return True, False
        elif pos in self.super_food:
            self.super_food.discard(pos)  
            return False, True
        
        return False, False


    def _update_snake_body(self, pos: tuple[int, int], body: list[list[int]], prev_body: list[list[int]], eat_food: bool, find_super_food: bool):
        if not prev_body: # Initial setup of the body 
            for segment in body:
                x, y = segment
                self.grid[x][y] = Tiles.SNAKE # Mark each body segment
            return
        
        if self.ate_super_food:
            # Clear previous snake from grid 
            for segment in prev_body:
                x, y = segment
                self.grid[x][y] = Tiles.VISITED if (x, y) not in self.stones else Tiles.STONE
            # Mark current snake in grid
            for segment in body:
                x, y = segment
                self.grid[x][y] = Tiles.SNAKE # Mark each body segment
        else:
            # Mark Head
            head_x, head_y = pos
            self.grid[head_x][head_y] = Tiles.SNAKE 

            # Remove Tail
            prev_tail = prev_body[-1]
            if not self.ate_food:
                prev_tail_x, prev_tail_y = prev_tail
                self.grid[prev_tail_x][prev_tail_y] = Tiles.VISITED if (prev_tail_x, prev_tail_y) not in self.stones else Tiles.STONE

        self.ate_food = True if eat_food == True else False
        self.ate_super_food = True if find_super_food == True else False
        

    def _update_visited_tiles(self, sight: dict[int, dict[int, Tiles]]):
        # Mark all cells as visited within sight if they are passages
        for x, y_tile in sight.items():
            for y, tile in y_tile.items():
                if tile == Tiles.PASSAGE:
                    self.grid[x][y] = Tiles.VISITED
            
            
    def clear_visited_tiles(self):
        """Clear all visited tiles."""
        for x in range(self.hor_tiles):
            for y in range(self.ver_tiles):
                if self.get_tile((x, y)) == Tiles.VISITED:
                    self.grid[x][y] = Tiles.PASSAGE


    def is_fully_explored(self) -> bool:
        """Check if the grid is fully explored (no more unexplored PASSAGE tiles)."""
        for x in range(self.hor_tiles):
            for y in range(self.ver_tiles):
                if self.grid[x][y] == Tiles.PASSAGE:
                    return False # Still Tiles to explore
        return True
    

    def get_zone(self, pos: tuple[int, int], size: int) -> dict[int, dict[int, Tiles]]:
        # TODO
        zone: dict[int, dict[int, Tiles]] = {}
        x, y = pos
        for i in range(x - size, x + size + 1):
            for j in range(y - size, y + size + 1):
                if math.dist((x, y), (i, j)) <= size:
                    ii = i % self.hor_tiles
                    jj = j % self.ver_tiles
                    if ii not in zone:
                        zone[ii] = {}
                    zone[ii][jj] = self.grid[ii][jj]
        return zone


    def is_blocked(self, position):
        x, y = position
        
        # Out of bounds
        if not self.traverse and (x not in range(self.hor_tiles) or y not in range(self.ver_tiles)):
            return True
        
        tile_type = self.get_tile(position)

        if tile_type in [Tiles.PASSAGE, Tiles.VISITED]:
            return False
        if tile_type == Tiles.STONE:
            return not self.traverse
        if tile_type == Tiles.SNAKE:
            return True
        if tile_type == Tiles.FOOD:
            return False
        if tile_type == Tiles.SUPER: # Dodges super foods when sight range = 6 (max)
            if Snake.range != 6:
                return False
            else:
                return True

        raise ValueError(f"Unknown tile type: {tile_type}")
        

    def calculate_pos(self, current: tuple[int, int], direction: Direction) -> tuple[int, int]:
        cur_x, cur_y = current
        dx, dy = {
            Direction.NORTH: (0, -1),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0),
            Direction.EAST: (1, 0)
        }[direction]

         # Calculate new position
        new_x, new_y = cur_x + dx, cur_y + dy

        # Apply wrap-around
        if self.traverse:
            new_x = new_x % self.hor_tiles 
            new_y = new_y % self.ver_tiles 

        new_pos = (new_x, new_y)

        # Ensure the position is not blocked
        return new_pos if not self.is_blocked(new_pos) else current
    

    def get_neighbours(self, actions: list[Direction], current_pos: tuple[int, int], current_direction: Direction) -> list[tuple[tuple[int, int], Direction]]:
        """Return neighbors of the current position, avoiding reverse direction."""
        map_opposite_direction = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }

        neighbours = set()

        for action in actions:
            # Avoid moving in the reverse direction
            if action == map_opposite_direction.get(current_direction):
                continue
            
            new_position = self.calculate_pos(current_pos, action)
            if current_pos != new_position:
                neighbours.add((new_position, action))

        return neighbours

    
    def print_grid(self):
        string_map_tile = {
            Tiles.PASSAGE: " ",
            Tiles.STONE: "X", 
            Tiles.FOOD: "F",
            Tiles.SUPER: "S",
            Tiles.SNAKE: "B",
            Tiles.VISITED: "."
        }

        for y in range(self.ver_tiles): 
            row = []
            for x in range(self.hor_tiles): 
                tile_value = self.grid[x][y]
                row.append(string_map_tile.get(tile_value, "?"))
            print(", ".join(row))
        

    
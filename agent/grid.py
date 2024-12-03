import math
import copy 

from typing import Union, Optional

from consts import Tiles, Direction

class Grid:
    def __init__(self, size: tuple[int, int], grid: list[list], age_update_rate: int = 1, slow_down_effect: int = 0):
        self._size = size
        self.grid = grid
            
        self.initialize_grid()
        self._stones = self._set_stones()
        self._food = self._set_foods()
        self._super_food = set()
        self._traverse = None

        self._prev_enemy_body = set()
        self._enemy_body = set()
        
        self._ate_food = False
        self._ate_super_food = False

        self._age_update_rate = age_update_rate # Allows Tiles to age every <age_update_rate> steps
        self._slow_down_effect = slow_down_effect # Allows Tiles within sight to age slower
        self._age_growth_rate = 1.12 # age *=  age_growth_rate

    def __repr__(self):
        return f"Grid(size={self.size}, stones={len(self.stones)} stones, food={len(self.food)} items, super_food={len(self.super_food)} items)"

    def __str__(self):
        return f"Grid - Size: {self.size}, Stones: {len(self.stones)}, Food: {len(self.food)}, Super Food: {len(self.super_food)}, Traverse: {self.traverse}"

    def __deepcopy__(self, memo):
        # First, create a new Grid instance with a deep copy of the grid list
        copied = Grid(self._size, copy.deepcopy(self.grid, memo))

        # Deep copy other attributes
        copied._stones = copy.deepcopy(self._stones, memo)
        copied._food = copy.deepcopy(self._food, memo)
        copied._super_food = copy.deepcopy(self._super_food, memo)
        copied._traverse = self._traverse  # If _traverse doesn't need deep copying, just copy the reference

        # Optionally, you can also copy other dynamic attributes if they exist
        copied._ate_food = self._ate_food
        copied._ate_super_food = self._ate_super_food
        copied._age_update_rate = self._age_update_rate
        copied._slow_down_effect = self._slow_down_effect

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
    def prev_enemy_body(self) -> set:
        return self._prev_enemy_body

    @property
    def enemy_body(self) -> set:
        return self._enemy_body

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
    def age_update_rate(self) -> int:
        return self._age_update_rate

    @age_update_rate.setter
    def age_update_rate(self, rate: int):
        if not isinstance(rate, int) or rate < 1:
            raise ValueError(f"Invalid value for age_update_rate: {rate}. Expected an integer greater than or equal to 1.")
        self._age_update_rate = rate

    @property
    def slow_down_effect(self) -> int:
        return self._slow_down_effect

    @slow_down_effect.setter
    def slow_down_effect(self, slow_down_effect: int):
        if not isinstance(slow_down_effect, int) or slow_down_effect < 0:
            raise ValueError(f"Invalid value for slow_down_effect: {slow_down_effect}. Expected a non negative integer.")
        self._slow_down_effect = slow_down_effect
    

    def initialize_grid(self):
        """Initialize the grid by converting all Tiles.PASSAGE to (Tiles.VISITED, age, slow_down_effect)."""
        self.grid = [
        [
            (Tiles.VISITED, 1, 0) if self.grid[x][y] == Tiles.PASSAGE else self.grid[x][y]
            for y in range(self.ver_tiles)
        ]
        for x in range(self.hor_tiles)
    ]
        
    def _set_stones(self) -> set[tuple[int, int]]:
        """Initialize the positions of stones on the grid."""
        return {(x, y) for x in range(self.hor_tiles) for y in range(self.ver_tiles) if self.grid[x][y] == Tiles.STONE}


    def _set_foods(self) -> set[tuple[int, int]]:
        """Initialize the positions of foods on the grid."""
        return {(x, y) for x in range(self.hor_tiles) for y in range(self.ver_tiles) if self.grid[x][y] == Tiles.FOOD}


    def get_tile(self, pos: tuple[int, int]) -> Union[Tiles, tuple[Tiles, float, int]]:
        """Return the tile type or tuple (Tiles.VISITED, age, slow_down_effect) at the given position."""
        x, y = pos
        return self.grid[x][y]
    

    def update(self, pos: tuple[int, int], prev_body: list[list[int]], body: list[list[int]], sight: dict[int, dict[int, Tiles]], traverse: bool, step: int):    
        self.traverse = traverse
        self._update_visited_tiles(sight, step) 
        eat_food, eat_super_food = self._update_food(pos, sight)
        self._update_snake_body(pos, prev_body, body, eat_food, eat_super_food)
        self._update_enemy_snake_body(body, sight)

        
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
                elif tile == Tiles.PASSAGE or tile == Tiles.SNAKE: 
                    if (x, y) in self._food:
                        self._food.remove((x, y))
                    elif (x, y) in self._super_food:
                        self._super_food.remove((x, y))
        
        # Eat food and super_food
        if pos in self.food:
            self.food.discard(pos)
            return True, False
        elif pos in self.super_food:
            self.super_food.discard(pos)  
            return False, True
        
        return False, False


    def _update_snake_body(self, pos: tuple[int, int], prev_body: list[tuple[int, int]], body: list[tuple[int, int]], eat_food: bool, eat_super_food: bool):
        """Updates the snake's body on the grid based on its current position and previous body."""
        if not prev_body: # Initial setup of the body 
            for segment in body:
                x, y = segment
                self.grid[x][y] = Tiles.SNAKE # Mark each body segment
            return
        
        if self.ate_super_food:
            # Clear previous snake from grid 
            for segment in prev_body:
                x, y = segment
                self.grid[x][y] = (Tiles.VISITED, 1, 0) if (x, y) not in self.stones else Tiles.STONE
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
                self.grid[prev_tail_x][prev_tail_y] = (Tiles.VISITED, 1, 0) if (prev_tail_x, prev_tail_y) not in self.stones else Tiles.STONE

        self.ate_food = True if eat_food == True else False
        self.ate_super_food = True if eat_super_food == True else False

    
    def _update_enemy_snake_body(self, body: list[list[int]], sight: dict[int, dict[int, Tiles]]):
        """Updates the snake's enemy body on the grid based on snake's sight."""
        
        # Clear previous enemy body
        for x, y in self.prev_enemy_body:
            self.grid[x][y] = (Tiles.VISITED, 1, 0) if (x, y) not in self.stones else Tiles.STONE
        
        self.prev_enemy_body.clear()

        # Mark the current enemy body
        for x, y_tile in sight.items():
            for y, tile in y_tile.items():
                if tile == Tiles.SNAKE and (x, y) not in body:
                    self.grid[x][y] = Tiles.ENEMY
                    self.prev_enemy_body.add((x, y))

        
    def update_snake_body(self, prev_body: set[tuple[int, int]], body: list[tuple[int, int]]):
        """Update snake body should only be used for deepcopies of grid"""
        # Clear snake
        for segment in prev_body:
            x, y = segment
            self.grid[x][y] = (Tiles.VISITED, 1, 0)

        # Mark snake body 
        for segment in body:
            x, y = segment
            self.grid[x][y] = Tiles.SNAKE
            

    def _update_visited_tiles(self, sight: dict[int, dict[int, Tiles]], step: int):    
        """
        Updates the aging of VISITED tiles on the grid and converts PASSAGE tiles within sight to VISITED.

        (Tiles.VISITED, age, slow_down_effect)

        This function performs two main actions:
        
        1. Increases the age of all VISITED tiles by 1 every `self.age_update_rate` steps. If a tile's
        `slow_down_effect` is greater than 0, the tile will decrement its `slow_down_effect` by 1 
        instead of aging, allowing tiles to age more slowly. Once the `slow_down_effect` reaches 0,
        the tile ages normally.
        
        2. Converts all PASSAGE tiles within the snake's sight to VISITED with an initial age of 1 and 
        a configurable slow down effect to delay their aging. This ensures that newly visited tiles start 
        with a uniform age and slow-down effect.

        Parameters:
        -----------
        sight : dict[int, dict[int, Tiles]]
            A dictionary representing the snake's current sight, where each key is an x-coordinate and
            each value is a nested dictionary with y-coordinates and their corresponding tile types.
            
        step : int
            The current game step, used to determine if aging should occur based on `age_update_rate`.
        
        Note:
        -----------
        - Use the self.slow_down_effect to control the rate of age of tiles within sight
        - Slow down effect is temporary
        """
        # Step 1: Increase the age of all visited tiles by 1 every `self.age_update_rate` steps
        if step % self.age_update_rate == 0: 
            for x in range(self.hor_tiles):
                for y in range(self.ver_tiles):
                    tile_value = self.grid[x][y]
                    if isinstance(tile_value, tuple) and tile_value[0] == Tiles.VISITED:
                        age, slow_down_effect = tile_value[1], tile_value[2]
                        if slow_down_effect > 0:
                            self.grid[x][y] = (Tiles.VISITED, age, slow_down_effect - 1)
                        else:
                            age *= self._age_growth_rate
                            self.grid[x][y] = (Tiles.VISITED, age, 0)
        
        # Step 2: Mark all PASSAGE tiles within sight as VISITED with age 1 and a fixed slow-down effect
        for x, y_tile in sight.items():
            for y, tile in y_tile.items():
                if tile == Tiles.PASSAGE:
                    self.grid[x][y] = (Tiles.VISITED, 1, self.slow_down_effect)
            
      
    def get_zone(self, pos: tuple[int, int], size: int) -> dict[int, dict[int, Tiles]]:
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

        if isinstance(tile_type, tuple) and tile_type[0] == Tiles.VISITED:
            return False
        if tile_type == Tiles.STONE:
            return not self.traverse
        if tile_type == Tiles.SNAKE or tile_type == Tiles.ENEMY:
            return True
        if tile_type in [Tiles.FOOD, Tiles.SUPER]:
            return False

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
    

    def get_neighbours(
            self, 
            actions: list[Direction], 
            current_pos: tuple[int, int], 
            current_direction: Direction, 
            ) -> list[tuple[tuple[int, int], Direction]]:
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

    
    def print_grid(self, snake_head: Optional[tuple[int, int]] = None, age: bool = False):
        string_map_tile = {
            Tiles.PASSAGE: " ",
            Tiles.STONE:   "X", 
            Tiles.FOOD:    "F",
            Tiles.SUPER:   "S",
            Tiles.SNAKE:   "B",
            Tiles.VISITED: ".",
            Tiles.ENEMY:   "E"
        }

        for y in range(self.ver_tiles): 
            row = []
            for x in range(self.hor_tiles): 
                if (x, y) == snake_head:
                    row.append('H')  # If it's the snake's head, print 'H'
                else:
                    tile_value = self.grid[x][y]
                    if isinstance(tile_value, tuple) and tile_value[0] == Tiles.VISITED:
                        row.append(f"{int(tile_value[1])}") if age else row.append(" ")
                    else:
                        row.append(string_map_tile.get(tile_value, "?"))
            print(", ".join(row))
        

    
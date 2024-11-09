import math
import copy 

from consts import Tiles, Direction

class Grid:
    def __init__(self, size: tuple[int, int], grid: list[list]):
        self._size = size
        self.grid = grid
        self._stones = self._set_stones()
        self._food = set() 
        self._super_food = set()
        self._traverse = None
        
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
    

    def update(self, pos: tuple[int, int], body: list[list[int]], sight: dict[int, dict[int, Tiles]], traverse: bool):    
        self.traverse = traverse
        self._update_food(pos, sight)
        self._set_visited_tiles(body, sight) 
        
    
    def _update_food(self, pos: tuple[int, int], sight: dict[int, dict[int, Tiles]]):
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
        pos_tile = self.get_tile(pos) 
        if pos_tile == Tiles.FOOD:
            self._food.discard(pos)  
            self.clear_visited_tiles() # Clear all visited cells
        elif pos_tile == Tiles.SUPER:
            self._super_food.discard(pos)  
            self.clear_visited_tiles() # Clear all visited cells
    

    def _set_visited_tiles(self, body: list[list[int]], sight: dict[int, dict[int, Tiles]]):
        # Mark all cells as visited if our snake is on them except for stones
        for segment in body:
            x, y = segment
            if self.get_tile(segment) == Tiles.STONE: continue
            self.grid[x][y] = Tiles.VISITED

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

    
    def print_grid(self):
        string_map_tile = {
            Tiles.PASSAGE: "P",
            Tiles.STONE: "X", 
            Tiles.FOOD: "F",
            Tiles.SUPER: "S",
            Tiles.SNAKE: "B",
            Tiles.VISITED: "V"
        }

        for y in range(self.ver_tiles): 
            row = []
            for x in range(self.hor_tiles): 
                tile_value = self.grid[x][y]
                row.append(string_map_tile.get(tile_value, "?"))
            print(", ".join(row))
        

    
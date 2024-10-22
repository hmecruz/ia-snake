import math
from consts import Tiles, Direction, Vector

class Grid:
    def __init__(self, size: tuple[int, int], grid: list[list], traverse: bool):
        self._size = size
        self.grid = grid
        self._stones = self._set_stones()
        self._food = []
        self._super_food = []
        self._traverse = traverse 
        
    
    @property
    def hor_tiles(self):
        return self._size[0]

    @property
    def ver_tiles(self):
        return self._size[1]

    @property
    def size(self):
        return self._size

    @property
    def stones(self):
        return self._stones

    @property
    def foods(self):
        return self._food
    
    @property
    def super_food(self):
        return self._super_food

    @property
    def traverse(self):
        return self._traverse
    
    @traverse.setter
    def traverse(self, traverse: bool):
        self._traverse = traverse


    def update(self, pos: tuple[int, int], sight: dict, traverse: bool):
        self.traverse(traverse)
        self._update_foods(pos, sight)
        

    def _set_stones(self):
        # TODO 
        # Get stones from the grid
        # If a Tile in the grid == Tiles.STONE
        # Retrieve the STONE position
        self._stones = []
        
    
    def _update_foods(self, pos: tuple[int, int], sight: dict):
        # TODO
        # Update food and super food position
        # Search for Tiles.FOOD | Tiles.SUPER
        # In case snake pos is equal to FOOD or SUPER FOOD remove it
        # Update grid
        pass
        
 
    def get_tile(self, pos: tuple[int, int]):
        x, y = pos
        return self.grid[x][y]
    
    
    def get_zone(self, pos: tuple[int, int], size: int):
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


    def is_blocked(self, pos, traverse):
        x, y = pos
        if not traverse and (
            x not in range(self.hor_tiles) or y not in range(self.ver_tiles)
        ):
            return True
        if self.grid[x][y] == Tiles.PASSAGE:
            return False
        if self.grid[x][y] == Tiles.STONE:
            if traverse:
                return False
            else:
                return True
        if self.grid[x][y] in [Tiles.FOOD, Tiles.SUPER]:
            return False

        assert False, "Unknown tile type"
        

    # TODO
    # Change calc_pos to use Vector instead of Direction
    def calc_pos(self, cur, direction: Direction, traverse=False):
        cx, cy = cur
        npos = cur
        if direction == Direction.NORTH:
            if traverse and cy - 1 < 0:  # wrap around
                npos = cx, self.ver_tiles - 1
            else:
                npos = cx, cy - 1
        if direction == Direction.WEST:
            if traverse and cx - 1 < 0:  # wrap around
                npos = self.hor_tiles - 1, cy
            else:
                npos = cx - 1, cy
        if direction == Direction.SOUTH:
            if traverse and cy + 1 >= self.ver_tiles:  # wrap around
                npos = cx, 0
            else:
                npos = cx, cy + 1
        if direction == Direction.EAST:
            if traverse and cx + 1 >= self.hor_tiles:  # wrap around
                npos = 0, cy
            else:
                npos = cx + 1, cy

        # test blocked
        if self.is_blocked(npos, traverse):
            return cur

        return npos

    
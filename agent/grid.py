import math
from consts import Tiles, Direction, Vector

class Grid:
    def __init__(self, size: tuple[int, int], grid: list[list], traverse: bool):
        self._size = size
        self.grid = grid
        self._stones = []
        self._foods = []
        self._super_foods = []
        self._traverse = traverse 
        
    
    @property
    def hor_tiles(self):
        return self.size[0]

    @property
    def ver_tiles(self):
        return self.size[1]

    @property
    def size(self):
        return self.size

    @property
    def stones(self):
        return self.stones

    @property
    def foods(self):
        return self.foods
    
    @property
    def super_foods(self):
        return self.super_foods

    @property
    def traverse(self):
        return self._traverse

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

    
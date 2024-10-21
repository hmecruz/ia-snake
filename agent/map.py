class Map:
    def __init__(self, size: tuple[int, int], map: list[list]):
        self.size = size
        self.map = map
        
        self.stones = []
        self.foods = []
        self.super_foods = []
        
    
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
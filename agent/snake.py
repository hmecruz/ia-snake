from consts import Direction

class Snake:
    def __init__(self):
        self.pos = None # Head position
        self.dir = None 
        self._body = None
        self._sight = None
        self._range = None
    
    @property
    def position(self):
        return self.pos
    
    @position.setter
    def position(self, new_position: tuple[int, int]):
        self.pos = new_position
        
    @property
    def direction(self):
        return self.direction
    
    @direction.setter
    def position(self, new_direction: Direction):
        self.direction = new_direction

    @property
    def body(self):
        return self._body
    
    @body.setter
    def body(self, new_body: list[tuple[int, int]]):
        self._body = new_body
    
    @property
    def sight(self):
        return self._sight
    
    @sight.setter
    def sight(self, new_sight: dict):
        self._sight = new_sight
    
    @property
    def range(self):
        return self._range
    
    @range.setter
    def range(self, new_range: int):
        self._range = new_range
import copy

from consts import Direction, Mode, Tiles

class Snake:
    def __init__(self):
        self._pos: tuple[int, int] = None  # Head position
        self._dir: Direction = None
        self._prev_body: list[tuple[int, int]] = None
        self._body: list[tuple[int, int]] = None
        self._sight: dict[int, dict[int, Tiles]] = None
        self._range: int = None
        self._mode: Mode = None
        self._eat_super_food: bool = False
    
    def __repr__(self):
        return (f"Snake(position={self.position}, direction={self.direction}, "
                f"body={self.body}, sight={self.sight}, range={self.range}, mode={self.mode})")
    
    def __str__(self):
        return (f"Snake - Position: {self.position}, Direction: {self.direction}, "
                f"Body Length: {len(self.body)} segments, Range: {self.range}, Mode: {self.mode}")
    
    def __deepcopy__(self, memo):
        copied = Snake()
        copied._pos = self._pos
        copied._dir = self._dir
        copied._mode = self._mode
        copied._body = copy.deepcopy(self._body, memo)
        copied._sight = copy.deepcopy(self._sight, memo)
        copied._range = self._range
        copied._eat_super_food = self._eat_super_food
        return copied

    @property
    def position(self) -> tuple[int, int]:
        return self._pos
    
    @position.setter
    def position(self, new_position: tuple[int, int]):
        if not isinstance(new_position, tuple) or len(new_position) != 2:
            raise ValueError(f"Invalid position format: Expected a tuple (x, y) with two integer values, but received {new_position}.")
        self._pos = new_position
        
    @property
    def direction(self) -> Direction:
        return self._dir
    
    @direction.setter
    def direction(self, new_direction: Direction):
        if not isinstance(new_direction, Direction):
            raise ValueError(f"Invalid direction: Expected a Direction enum value, but received {new_direction}.")
        self._dir = new_direction

    @property
    def prev_body(self) -> list[tuple[int, int]]:
        return self._prev_body

    @prev_body.setter
    def prev_body(self, old_body: list[tuple[int, int]]):
        self._prev_body = old_body

    @property
    def body(self) -> list[tuple[int, int]]:
        return self._body
    
    @body.setter
    def body(self, new_body: list[list[int]]):
        if not (
            isinstance(new_body, list) and 
            all(isinstance(part, list) and len(part) == 2 and all(isinstance(coord, int) for coord in part) for part in new_body)
        ):
            raise ValueError(f"Invalid body format: Expected a list of [x, y] positions with integer values, but received {new_body}.")
        self._body = [tuple(segment) for segment in new_body]


    @property
    def size(self) -> int:
        return len(self._body)

    @property
    def sight(self) -> dict[int, dict[int, Tiles]]:
        return self._sight
    
    @sight.setter
    def sight(self, new_sight: dict[int, dict[int, Tiles]]):
        if not isinstance(new_sight, dict):
            raise ValueError(f"Invalid sight format: Expected a dictionary of dictionaries with Tiles, but received {new_sight}.")
        self._sight = new_sight
    
    @property
    def range(self) -> int:
        return self._range
    
    @range.setter
    def range(self, new_range: int):
        if not isinstance(new_range, int) or new_range < 2 or new_range > 6:
            raise ValueError(f"Invalid range value: Expected a integer between 2 and 6 inclusive, but received {new_range}.")
        self._range = new_range

    @property
    def mode(self) -> Mode:
        return self._mode
    
    @mode.setter
    def mode(self, new_mode: Mode):
        if not isinstance(new_mode, Mode):
            raise ValueError(f"Invalid mode: Expected a Mode enum value, but received {new_mode}.")
        self._mode= new_mode

    @property
    def eat_super_food(self) -> bool:
        return self._eat_super_food
    
    @eat_super_food.setter
    def eat_super_food(self, eat_super_food: bool):
        if not isinstance(eat_super_food, bool):
            raise ValueError(f"Invalid eat_super_food: Expected a Boolean, but received {eat_super_food}.")
        self._eat_super_food = eat_super_food
    

    def update(
            self, 
            pos: tuple[int, int], 
            dir: Direction, 
            body: list[list[int]], 
            sight: dict[int, dict[int, Tiles]], 
            range: int,
            eat_super_food: bool = False
        ):
        
        self.position = pos
        self.direction = dir
        self.prev_body = self.body
        self.body = body
        self.sight = sight
        self.range = range
        self.eat_super_food = eat_super_food


    def move(self, direction: Direction) -> str:
        direction_to_key = {
            Direction.NORTH: "w",  
            Direction.SOUTH: "s",   
            Direction.WEST : "a",  
            Direction.EAST : "d"    
        }

        if direction not in direction_to_key:
            raise ValueError(f"Invalid move: Direction {direction._name_} current Direction {self.direction._name_}.")
        return direction_to_key.get(direction, ' ')
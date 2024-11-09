from ..grid import Grid
from ..snake import Snake
from consts import Direction, Tiles, Mode

class SnakeDomain():
    
    def __init__(self, snake: Snake, grid: Grid):
        self.snake = snake
        self.grid = grid


    def actions(self, state) -> set[Direction]:
        actions = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]
        possible_actions = set()

        for action in actions:
            if self.is_action_valid(state, action):
                possible_actions.add(action)
        return possible_actions

        
    def result(self, state: tuple[int, int], action: Direction) -> tuple[int, int]:
        return self.grid.calc_pos(state, action, self.grid.traverse)
        
        
    def cost(self, state: tuple[int, int], action: Direction) -> int:        
        new_pos = self.result(state, action)
        if self.grid.get_tile(new_pos) == Tiles.VISITED:
            return 10 # Can be changed
        return 1
        

    def heuristic(self, state: tuple[int, int], goal: tuple[int, int] | None) -> int:
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

    
    def satisfies(self, state: tuple[int, int], goal: tuple[int, int] | None) -> bool:
        return state == goal 


    def is_action_valid(self, state: tuple[int, int], action: Direction) -> bool:
        map_opposite_direction = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }

        if action == map_opposite_direction.get(self.snake.direction): # Snake can't move to the opposite direction of its current direction
            return False 
        
        # Calculate the new position based on the action
        new_position = self.grid.calc_pos(state, action, self.grid.traverse)

        # Check if the new position is the same as the current position
        if state == new_position:
            return False

        return True
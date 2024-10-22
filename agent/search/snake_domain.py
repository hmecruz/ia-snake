from tree_search import SearchDomain
from grid import Grid
from snake import Snake
from consts import Direction, Vector

class SnakeDomain(SearchDomain):
    
    def __init__(self, snake: Snake, grid: Grid):
        self.snake = snake
        self.grid = grid

    def actions(self) -> list[Vector]:
        actions = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]
        possible_actions = set()


        for action in actions:
            if self.is_action_valid(action):
                possible_actions.add(action)

        return possible_actions

        
    def result(self, action):
        return self.grid.calc_pos(self.snake.position, action,self.grid.traverse)
        
        
    def cost(self, state, action):
        # Cost is always one for now
        # Action is a move from a node to the next or previous node
        # Equivalent to moving in one of 3 directions (Can't move backward)
        pass
        

    def heuristic(self, state, goal):
        # Manhatam distance 
        # We can add more heuristic and do the Max euristic (thereotical classes)
        pass

    def satisfies(self, state, goal):
        # Test if the state and the goal are equal
        pass



    def is_action_valid(self, action: Direction) -> bool:
        map_opposite_direction = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }

        if action == map_opposite_direction.get(self.snake.direction): # Snake can't move to the opposite direction of its current direction
            return False 
        
        # Calculate the new position based on the action
        new_position = self.grid.calc_pos(self.snake.position, action, self.grid.traverse)

        # Check if the new position is the same as the current position
        if self.snake.position == new_position:
            return False

        return True
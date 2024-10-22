from tree_search import SearchDomain
from grid import Grid
from snake import Snake
from consts import Tiles, Direction, Vector

class SnakeDomain(SearchDomain):
    
    def __init__(self, snake: Snake, grid: Grid):
        self.snake = snake
        self.grid = grid

    def actions(self):
        actions = [Vector.NORTH, Vector.SOUTH, Vector.WEST, Vector.EAST]
        # TODO
        
    def result(self, action):
        self.grid.calc_pos(
            self.snake.position, 
            action,
            self.grid.traverse
            )
        
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
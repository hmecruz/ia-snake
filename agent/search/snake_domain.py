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
        # Todo
        pass
        
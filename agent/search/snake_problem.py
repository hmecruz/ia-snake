from ..grid import Grid
from ..snake import Snake

"""
SnakeProblem:
1 - Problem is composed by the snake initial position and the goal position
2 - This class should analyse, with the given information, what is the next goal position
3 - You may and should use other classes, methods, functions in order to discover what is the next goal position
"""

class SnakeProblem():
    def __init__(self, snake: Snake, grid: Grid):
        self.snake = snake
        self.grid = grid

    def problem(self) -> tuple[tuple[int, int], tuple[int, int]]:
        # Return initial, goal
        # This function should analyse the mode the robot should be in, exploration mode...
        # It should provide the necessary information, in order to retrieve the goal position
        return

    
    
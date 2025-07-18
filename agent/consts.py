from enum import IntEnum


class Tiles(IntEnum):
    PASSAGE = 0
    STONE = 1
    FOOD = 2
    SUPER = 3
    SNAKE = 4
    VISITED = 5
    BLOCKED = 6
    ENEMY = 7
    ENEMY_SUPPOSITION = 8


class SuperFood(IntEnum):
    POINTS = 1
    LENGTH = 2
    RANGE = 3
    TRAVERSE = 4


class Speed(IntEnum):
    SLOWEST = (1,)
    SLOW = (2,)
    NORMAL = (3,)
    FAST = 4


class Direction(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    

class Mode(IntEnum):
    EXPLORATION = 0 # Searching for food or enemy snake 
    EATING = 1 # Trying to reach food
    ATTACK = 2 # Attack other snakes
    DEFEND = 3 # Defend against other snakes
    SURVIVAL = 4 # Just try to survive by not getting trapped
    REGROUP = 5 # Snake regroups if its too spread 
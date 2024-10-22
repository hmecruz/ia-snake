from consts import Direction

def determine_direction(
        current_pos: tuple[int, int], next_pos: tuple[int, int]
        ) -> Direction:
    
    if next_pos[0] < current_pos[0]:
        return Direction.WEST
    elif next_pos[0] > current_pos[0]:
        return Direction.EAST
    elif next_pos[1] < current_pos[1]:
        return Direction.NORTH
    elif next_pos[1] > current_pos[1]:
        return Direction.SOUTH
    else:
        return None
        
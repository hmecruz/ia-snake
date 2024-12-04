import time
from consts import Direction, Tiles

def set_start_time():
    global start_time
    start_time = time.time()

def get_start_time():
    return start_time

def determine_direction(
        current_pos: tuple[int, int], next_pos: tuple[int, int], grid_size: tuple[int, int]
        ) -> Direction:
    """Calculates the direction based on two adjacent positions"""

    if next_pos == current_pos:
        return None
    
    cur_x, cur_y = current_pos
    next_x, next_y = next_pos

    dx = next_x - cur_x 
    dy = next_y - cur_y

    # Direction lookup for non-wrap cases
    direction_map = {
        (0, -1): Direction.NORTH,
        (0, 1): Direction.SOUTH,
        (-1, 0): Direction.WEST,
        (1, 0): Direction.EAST
    }

    # Check for a direct direction
    if (dx, dy) in direction_map:
        return direction_map[(dx, dy)]
    
    # Direction lookup for wrap cases
    grid_width, grid_height = grid_size
    wrap_x = grid_width - 1
    wrap_y = grid_height - 1

    if dx == wrap_x:
        return Direction.WEST  # Wrap from right to left
    if dx == -wrap_x:
        return Direction.EAST  # Wrap from left to right
    if dy == wrap_y:
        return Direction.NORTH  # Wrap from bottom to top
    if dy == -wrap_y:
        return Direction.SOUTH  # Wrap from top to bottom

    raise ValueError(f"Position: {current_pos} is not adjacent to {next_pos}")

def convert_sight(sight: dict[str, dict[str, Tiles]]) -> dict[int, dict[int, Tiles]]:
    return {
        int(x): {int(y): tile for y, tile in y_tile.items()}
        for x, y_tile in sight.items()
    }


def compute_next_position(pos: tuple[int, int], direction: Direction, grid_size: tuple[int, int], grid_traverse: bool) -> tuple[int, int]:
    "Computes the next poosition based on a given Direction"
    x, y = pos
   
    map_dir_vector = {
        Direction.NORTH: (0, -1),
        Direction.SOUTH: (0, 1),
        Direction.WEST: (-1, 0),
        Direction.EAST: (1, 0)
    }
    dx, dy = map_dir_vector[direction]
    new_x, new_y = x + dx, y + dy

    grid_width, grid_height = grid_size

    # Apply wrap-around if grid_traverse is enabled
    if grid_traverse:
        new_x %= grid_width
        new_y %= grid_height
    
    if not (0 <= new_x < grid_width) or not (0 <= new_y < grid_height):
        raise ValueError(
        f"Next position {new_x, new_y} is out of bounds in a grid of size {grid_size}. "
        f"Current position: {pos}, Direction: {direction._name_}. "
        )
    
    return (new_x, new_y)


def compute_position_from_vector(pos: tuple[int, int], vector: tuple[int, int], grid_size: tuple[int, int], grid_traverse: bool) -> tuple[int, int]:
    """Computes the next position based on a position and a vector (dx, dy)."""
    x, y = pos
    dx, dy = vector  # Extract the vector components

    # Calculate the new position
    new_x, new_y = x + dx, y + dy

    grid_width, grid_height = grid_size

    # Apply wrap-around if grid_traverse is enabled
    if grid_traverse:
        new_x %= grid_width
        new_y %= grid_height
    
    if not (0 <= new_x < grid_width) or not (0 <= new_y < grid_height):
        raise ValueError(
            f"Next position {new_x, new_y} is out of bounds in a grid of size {grid_size}. "
            f"Current position: {pos}, Vector: {vector}. "
        )
    
    return (new_x, new_y)

def compute_body(next_pos: tuple[int, int], body: list[tuple[int, int]]) -> list[tuple[int, int]]:
    new_body = [next_pos] + body[:-1]  # Add new head and remove the last element (tail)
    return new_body

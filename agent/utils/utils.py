from consts import Direction, Tiles

def determine_direction(
        current_pos: tuple[int, int], next_pos: tuple[int, int], grid_size: tuple[int, int]
        ) -> Direction:
    """Calculates the direction based on two adjacent positions"""

    if next_pos == current_pos:
        return None
    
    cur_x, cur_y = current_pos
    next_x, next_y = next_pos

    cur_x, cur_y = current_pos
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
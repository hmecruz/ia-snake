from tree_search import SearchDomain

class SnakeDomain(SearchDomain):
    
    def __init__(self, grid_size, obstacles):
        """
        :param grid_size: A tuple representing the dimensions of the grid (rows, cols)
        :param obstacles: A list of coordinates representing obstacles on the grid
        """
        self.grid_size = grid_size
        self.obstacles = obstacles

    def actions(self, state):
        """
        Returns the list of possible actions (up, down, left, right) that can be taken from the current state.
        :param state: Current state of the snake (head position, body positions)
        :return: List of valid actions ('up', 'down', 'left', 'right')
        """
        head = state[0]
        body = state[1:]
        possible_actions = ['up', 'down', 'left', 'right']
        valid_actions = []

        for action in possible_actions:
            next_head = self.result(head, action)

            # Check if the new head position is inside the grid and not an obstacle or body part
            if self.is_valid_position(next_head, body):
                valid_actions.append(action)

        return valid_actions

    def result(self, state, action):
        """
        Returns the new state (new head position) after taking an action.
        :param state: Current head position (x, y)
        :param action: Action to take ('up', 'down', 'left', 'right')
        :return: New head position (x, y)
        """
        x, y = state[0]
        if action == 'up':
            return (x, y + 1), state[:-1]  # Move up and update body
        elif action == 'down':
            return (x, y - 1), state[:-1]  # Move down
        elif action == 'left':
            return (x - 1, y), state[:-1]  # Move left
        elif action == 'right':
            return (x + 1, y), state[:-1]  # Move right

    def cost(self, state, action):
        """
        Returns the cost of performing an action. For now, we assume a uniform cost of 1 for all moves.
        :param state: Current state (head position, body positions)
        :param action: Action to take
        :return: Cost of taking the action
        """
        return 1  # Uniform cost for every movement

    def heuristic(self, state, goal):
        """
        Returns the Manhattan distance from the snake's head to the goal position.
        :param state: Current state of the snake (head position, body positions)
        :param goal: Goal position (x, y)
        :return: Heuristic estimate (Manhattan distance) to the goal
        """
        head = state[0]
        return abs(head[0] - goal[0]) + abs(head[1] - goal[1])

    def satisfies(self, state, goal):
        """
        Checks if the current state satisfies the goal condition (snake's head reaches the goal).
        :param state: Current state (head position, body positions)
        :param goal: Goal position (x, y)
        :return: True if goal is satisfied, False otherwise
        """
        head = state[0]
        return head == goal

    def is_valid_position(self, position, body):
        """
        Check if a position is valid: within the grid, not an obstacle, and not part of the snake's body.
        :param position: Position to check (x, y)
        :param body: List of positions occupied by the snake's body
        :return: True if the position is valid, False otherwise
        """
        x, y = position
        # Check if the position is within the grid and not an obstacle or body part
        if (0 <= x < self.grid_size[0]) and (0 <= y < self.grid_size[1]) and position not in self.obstacles and position not in body:
            return True
        return False

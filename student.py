import os
import json
import time
import argparse
import websockets
import asyncio
import getpass

from collections import deque

from agent.snake import Snake
from agent.grid import Grid

from agent.search.exploration_dijkstra import Exploration
from agent.search.eating import Eating
from agent.search.death_circle import Survival

from agent.utils.utils import determine_direction, convert_sight, set_start_time, get_start_time

from consts import Mode, Tiles

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        state = json.loads(await websocket.recv()) 
        size = state["size"]
        grid = state["map"]
        
        snake = Snake()
        grid = Grid(size, grid, 5, 5)
        
        exploration = Exploration()
        eating = Eating()
        survival = Survival()

        path = deque()

        prev_food_positions = None
        prev_super_food_positions = None

        path_counter = 0
        path_clear_threshold = 2 # Path clear if path counter is bigger or equal to path_clear_threshold
        
        while True:
            try:
                state = json.loads(await websocket.recv()) 
                set_start_time()

                # Previous Assignments
                prev_mode = snake.mode
                prev_food_positions = grid.food.copy() # Shallow copy, elements inside are tuples (immutable)
                prev_super_food_positions = grid.super_food.copy() # Shallow copy, elements inside are tuples (immutable)

                update_snake_grid(state, snake, grid)

                # Path Clearence Conditions
                # TODO --> Make this a function in the future if it gets bigger (it will)
                if path:
                    if prev_mode != snake.mode:
                        path.clear() # Clear path if mode switches
                    elif prev_food_positions != grid.food:
                        path.clear() # Clear path if new food is found. Allows for path recalculation for closer foods
                    elif prev_super_food_positions != grid.super_food and snake.eat_super_food:
                        path.clear() # Clear path if new super food is found and eat super food is True. Allows for path recalculation for closer super foods
                    elif path_counter >= path_clear_threshold:
                        path.clear()
                    else:
                        if grid.enemies_exist: # Enemies are present
                            path.clear()

                # Path Calculation
                if not path: # List if empty
                    if snake.mode == Mode.EXPLORATION: 
                        path = exploration.get_path(snake, grid, True) # Request a new path to follow
                    elif snake.mode == Mode.EATING:
                        path = eating.get_path(snake, grid) # Request a new path to follow
                        if not path:
                            snake.mode = Mode.EXPLORATION # Default mode
                            path = exploration.get_path(snake, grid, True) # Request a new path to follow
                    if not path: 
                        snake.mode = Mode.SURVIVAL # Fallback mode
                        path = survival.get_path(snake, grid, 2)
                        
                    path_counter = 0 # Path counter reset

                
                if path:
                    direction = determine_direction(snake.position, path.popleft(), grid.size)
                    key = snake.move(direction)
                
                path_counter = path_counter + 1

                await websocket.send(json.dumps({"cmd": "key", "key": key}))

                # added
                enemy_previous_positions = set()
                enemy_previous_supposed_positions = set()
                enemy_current_positions = set()
                enemy_current_supposed_positions = set()
                if snake.prev_sight != None:
                    for i in snake._prev_sight:
                        for j in snake._prev_sight[i]:
                            if snake._prev_sight[i][j] == Tiles.ENEMY:
                                enemy_previous_positions.add((i, j))
                            elif snake._prev_sight[i][j] == Tiles.ENEMY_SUPPOSITION:
                                enemy_previous_supposed_positions.add((i, j))

                if snake.sight != None:
                    for i in snake._sight:
                        for j in snake._sight[i]:
                            if snake._sight[i][j] == Tiles.ENEMY:
                                enemy_current_positions.add((i, j))
                            elif snake._sight[i][j] == Tiles.ENEMY_SUPPOSITION:
                                enemy_current_supposed_positions.add((i, j))
                
                print(enemy_previous_positions)
                print(enemy_current_positions)
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            except ValueError:
                if path:   
                   path.clear()
            except Exception:
                if path:
                   path.clear()
            except Exception:
                pass
                

def update_snake_grid(state: dict, snake: Snake, grid: Grid):
    """Update the snake and grid objects based on the new game state."""
    body = state["body"]
    pos = tuple(body[0])
    direction = determine_direction(body[1], body[0], grid.size)
    sight = state["sight"]
    sight = convert_sight(sight) 
    range = state["range"]
    traverse = state["traverse"]

    step = state["step"]
    
    # Always update snake first
    snake.update(pos, direction, body, sight, range)
    grid.update(snake, traverse, step)
    snake_mode(snake, grid.food, grid.super_food, traverse, range, step)


def snake_mode(snake: Snake, grid_food: set[tuple[int, int]], grid_super_food: set[tuple[int, int]], traverse: bool, range: int, step: int):
    # Super food consumption strategy based on sight and traverse
    if step >= 2800:
        snake.eat_super_food = bool(grid_super_food)
    elif range >= 5 and traverse: 
        snake.eat_super_food = False  
    elif range == 3 and traverse or range >= 4:
        snake.eat_super_food = len(grid_super_food) >= 4 # Eat super food if enough food have been accumulated
    elif range < 3 or not traverse:
        snake.eat_super_food = bool(grid_super_food)

    if grid_food:
        snake.mode = Mode.EATING  # Prioritize normal food if available
    elif snake.eat_super_food:
        snake.mode = Mode.EATING
    else:
        snake.mode = Mode.EXPLORATION  # Default to exploration mode

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
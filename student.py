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

from agent.utils.utils import determine_direction, convert_sight

from consts import Mode


async def agent_loop(server_address="localhost:8000", agent_name="student", file_name=None):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        state = json.loads(await websocket.recv()) 
        size = state["size"]
        grid = state["map"]
        
        snake = Snake()
        grid = Grid(size, grid, 5, 5)
        exploration = Exploration()
        eating = Eating()

        path = deque()

        prev_body = None
        prev_food_positions = None
        prev_super_food_positions = None

        food_counter = 1
        food_step = 0
        steps_per_food = deque()
        
        while True:
            try:
                print("\n--------------------------------------------\n")
                state = json.loads(await websocket.recv()) 
                #start_time = time.time()

                current_step = state["step"]

                # Previous Assignments
                prev_mode = snake.mode
                if snake.body: prev_body = snake.body.copy() # Shallow copy, elements inside are tuples (immutable)
                prev_food_positions = grid.food.copy() # Shallow copy, elements inside are tuples (immutable)
                prev_super_food_positions = grid.super_food.copy() # Shallow copy, elements inside are tuples (immutable)

                update_snake_grid(state, snake, grid, prev_body)
                
                print(f"Snake Position: {snake.position}")
                print(f"Snake Direction: {snake.direction._name_}")
                print(f"Grid Traverse: {grid.traverse}")
                print(f"Sight Range: {snake.range}")
                print(f"Snake Mode: {snake.mode._name_}")
                print(f"Foods: {grid.food}")
                #print(f"Previous Foods: {prev_food_positions}")
                print(f"Super Foods: {grid.super_food}")
                print(f"Eat Super Food: {snake.eat_super_food}")
                #print(f"Snake Body: {snake.body}")
                print(f"Snake Size: {snake.size}")

                
                # Path Clearence Conditions --> TODO Make this a function in the future if it gets bigger (it will)
                if prev_mode != snake.mode:
                    path.clear() # Clear path if mode switches
                elif len(prev_food_positions) != len(grid.food):
                    path.clear() # Clear path if new food is found. Allows for path recalculation to closer food
                elif len(prev_super_food_positions) != len(grid.super_food) and snake.eat_super_food:
                    path.clear() # Clear path if new super food is found and eat super food is True. Allows for path recalculation to closer super foods


                # Path Calculation
                if not path: # List if empty
                    if snake.mode == Mode.EXPLORATION: 
                        path = deque(exploration.get_path(snake, grid, True)) # Request a new path to follow
                    elif snake.mode == Mode.EATING:
                        path = deque(eating.get_path(snake, grid)) # Request a new path to follow
                    
                print(f"Path: {path}")
                
                if path:
                    direction = determine_direction(snake.position, path.popleft(), grid.size)
                    key = snake.move(direction)

                if file_name and grid.ate_food:
                    (food_counter, current_step - food_step)
                    steps_per_food.append((food_counter, current_step - food_step))
                    food_step = current_step
                    food_counter += 1

            
                print(f"Key: {key}")  
                grid.print_grid(snake.position)
                
                #end_time = time.time()
                #duration_ms = (end_time - start_time) * 1000
                #print(f"Processing time: {duration_ms:.2f} ms")
                await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            except Exception as e:
                grid.print_grid(snake.position)
                if file_name:
                    export_steps_per_food(file_name, steps_per_food)
                raise e
                

def update_snake_grid(state: dict, snake: Snake, grid: Grid, prev_body: list[list[int]]):
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
    grid.update(pos, snake.body, snake.size, prev_body, snake.sight, traverse, step)
    snake_mode(snake, grid.food, grid.super_food, traverse, range)


def snake_mode(snake: Snake, grid_food: set[tuple[int, int]], grid_super_food: set[tuple[int, int]], traverse: bool, range: int):
    if grid_food:
        snake.mode = Mode.EATING
    elif not traverse or range < 4:
        snake.eat_super_food = True
        snake.mode = Mode.EATING if grid_super_food else Mode.EXPLORATION
    else:
        snake.mode = Mode.EXPLORATION  # Default mode

def export_steps_per_food(file_name: str, steps_per_food: deque[tuple[int, int]]):
    dir = './data'
    os.makedirs(dir, exist_ok=True)

    file_path = os.path.join(dir, file_name)

    with open(file_path, 'a') as json_file:
        json.dump(list(steps_per_food), json_file, indent=4)
        json_file.write("\n") 
    
    print(f"Steps data saved to {file_path}")


# TODO --> Uncomment this for the delivery
"""
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
"""

# TODO --> Comment this for the delivery
if __name__ == "__main__":
    # Parse command line arguments for file name
    parser = argparse.ArgumentParser(description="Run Snake agent")
    parser.add_argument('-out', '--output', type=str, required=False, help="Output file name for steps data")
    args = parser.parse_args()

loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME, args.output))
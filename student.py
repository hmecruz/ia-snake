import asyncio
import getpass
import json
import os
import websockets

from agent.snake import Snake
from agent.grid import Grid

from agent.search.exploration import Exploration
from agent.search.eating import Eating

from agent.utils.utils import determine_direction, convert_sight

from consts import Mode


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        state = json.loads(await websocket.recv()) 
        size = state["size"]
        grid = state["map"]
        
        snake = Snake()
        grid = Grid(size, grid)
        exploration = Exploration()
        eating = Eating()

        path = []
        prev_body = None
        
        while True:
            try:
                print("\n--------------------------------------------\n")
                state = json.loads(await websocket.recv()) 
                prev_mode = snake.mode
                if snake.body: prev_body = snake.body
                update_snake_grid(state, snake, grid, prev_body)

                print(f"Snake Position: {snake.position}")
                print(f"Snake Direction: {snake.direction._name_}")
                print(f"Grid Traverse: {grid.traverse}")
                print(f"Snake Mode: {snake.mode._name_}")
                print(f"Foods: {grid.food}")
                print(f"Snake Body: {snake.body}")
                
                if prev_mode != snake.mode:
                    path = [] # Clear path if mode switches

                if not path: # List if empty
                    if snake.mode == Mode.EXPLORATION: 
                        path = exploration.get_path(snake, grid) # Request a new path to follow
                    elif snake.mode == Mode.EATING:
                        path = eating.get_path(snake, grid) # Request a new path to follow
                    if path:
                        print(f"Path: {path}")
                
                if path:
                    direction = determine_direction(snake.position, path.pop(0), grid.size)
                    key = snake.move(direction)
            
                print(f"Key: {key}")  
                grid.print_grid()
                await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def update_snake_grid(state: dict, snake: Snake, grid: Grid, prev_body: list[list[int]]):
    """Update the snake and grid objects based on the new game state."""
    body = state["body"]
    pos = tuple(body[0])
    direction = determine_direction(body[1], body[0], grid.size)
    sight = state["sight"]
    sight = convert_sight(sight) 
    range = state["range"]
    traverse = state["traverse"]
    
    # Always update snake first
    snake.update(pos, direction, body, sight, range)
    grid.update(pos, body, prev_body, snake.sight, traverse)
    snake.mode = snake_mode(grid)


def snake_mode(grid: Grid):
    if grid.food:
        return Mode.EATING
    return Mode.EXPLORATION

            
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))


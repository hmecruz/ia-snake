import asyncio
import getpass
import json
import os
import websockets

from agent.snake import Snake
from agent.grid import Grid

from agent.search.exploration import Exploration

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

        path = []
        
        while True:
            try:
                print("\n--------------------------------------------\n")
                state = json.loads(await websocket.recv()) 
                update_snake_grid(state, snake, grid)

                print(f"Snake Position: {snake.position}")
                print(f"Snake Direction: {snake.direction._name_}")
                print(f"Grid Traverse: {grid.traverse}")
   
                if not path: # List if empty
                    path = exploration.get_path(snake, grid) # Request a new path to follow
                    if path:
                        print(f"Path: {path}")
                
                if path:
                    direction = determine_direction(snake.position, path.pop(0), (grid.hor_tiles, grid.ver_tiles))
                    key = snake.move(direction)
            
                print(f"Key: {key}")  
                grid.print_grid()
                await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def update_snake_grid(state: dict, snake: Snake, grid: Grid):
    """Update the snake and grid objects based on the new game state."""
    body = state["body"]
    pos = tuple(body[0])
    direction = determine_direction(body[1], body[0], (grid.hor_tiles, grid.ver_tiles))
    sight = state["sight"]
    sight = convert_sight(sight) 
    range = state["range"]
    traverse = state["traverse"]
    
    # Always update snake first
    snake.update(pos, direction, body, sight, range, mode=Mode.EXPLORATION)
    grid.update(pos, body, snake.sight, traverse)
            
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))


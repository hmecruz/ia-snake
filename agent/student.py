import asyncio
import getpass
import json
import os
import websockets

from .snake import Snake
from .grid import Grid

from .utils.utils import determine_direction


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        state = json.loads(await websocket.recv()) 
        size = state["size"]
        grid = state["map"]
        
        snake = Snake()
        grid = Grid(size, grid)

        while True:
            try:
                state = json.loads(await websocket.recv()) 
                
                update_snake_grid(state, snake, grid)

                key = "w"
                await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


def update_snake_grid(state: dict, snake: Snake, grid: Grid):
    """Update the snake and grid objects based on the new game state."""
    body = state["body"]
    pos = tuple(body[0])
    direction = determine_direction(body[1], body[0]) if len(body) > 1 else None
    sight = state["sight"]
    range = state["range"]
    traverse = state["traverse"]

    snake.update(pos, direction, body, sight, range)
    grid.update(pos, sight, traverse)

            
# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
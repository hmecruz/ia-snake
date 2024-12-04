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

from agent.utils.utils import determine_direction, convert_sight, set_start_time, get_start_time

from consts import Mode, Tiles

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

        prev_food_positions = None
        prev_super_food_positions = None

        food_counter = 1
        food_step = 0
        steps_per_food = deque()

        path_counter = 0
        path_clear_threshold = 2 # Path clear if path counter is bigger or equal to path_clear_threshold
        
        while True:
            try:
                print("\n--------------------------------------------\n")
                state = json.loads(await websocket.recv()) 
                set_start_time()

                current_step = state["step"]

                # Previous Assignments
                prev_mode = snake.mode
                prev_food_positions = grid.food.copy() # Shallow copy, elements inside are tuples (immutable)
                prev_super_food_positions = grid.super_food.copy() # Shallow copy, elements inside are tuples (immutable)

                update_snake_grid(state, snake, grid)
                
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
                #print(f"Snake Body: {snake.prev_body}")
                print(f"Snake Size: {snake.size}")

                #Path Clearence Conditions
                # TODO --> Make this a function in the future if it gets bigger (it will)
                if prev_mode != snake.mode:
                    path.clear() # Clear path if mode switches
                elif prev_food_positions != grid.food:
                    path.clear() # Clear path if new food is found. Allows for path recalculation for closer foods
                elif prev_super_food_positions != grid.super_food and snake.eat_super_food:
                    path.clear() # Clear path if new super food is found and eat super food is True. Allows for path recalculation for closer super foods
                elif path_counter >= path_clear_threshold:
                    path.clear()
                elif path:
                    # Prevent making impossible or danger moves due to enemies imprevisibility
                    direction = determine_direction(snake.position, path[0], grid.size)
                    x, y = grid.calculate_pos(snake.position, direction)
                    if grid.get_tile((x, y)) == Tiles.ENEMY_SUPPOSITION:
                        path.clear()
                    if grid.get_tile((x, y)) == Tiles.ENEMY:
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
                        snake.mode = Mode.EXPLORATION # Default mode
                        path = exploration.get_path(snake, grid, True, 1.1, flood_fill=False) # Request a new path to follow as last resort till death circle is implemented
                    path_counter = 0

                print(f"Path: {path}")
                
                if path:
                    direction = determine_direction(snake.position, path.popleft(), grid.size)
                    key = snake.move(direction)
                

                # Graph to keep the track of average food per step
                if file_name and grid.ate_food:
                    (food_counter, current_step - food_step)
                    steps_per_food.append((food_counter, current_step - food_step))
                    food_step = current_step
                    food_counter += 1

                # Debug
                print(f"Key: {key}")  
                path_counter = path_counter + 1
                grid.print_grid(snake.position) 
                
                # Processing time
                end_time = time.time()
                duration_ms = (end_time - get_start_time()) * 1000
                print(f"Processing time: {duration_ms:.2f} ms")
                print(f"Step: {state["step"]}")
                
                await websocket.send(json.dumps({"cmd": "key", "key": key}))  
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            #except ValueError:
                if path:   
                   path.clear()
            except Exception as e:
                grid.print_grid(snake.position)
                if file_name:
                    export_steps_per_food(file_name, steps_per_food)
                export_num_foods_eaten(food_counter)
                raise e
                

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

def export_steps_per_food(file_name: str, steps_per_food: deque[tuple[int, int]]):
    dir = './data'
    os.makedirs(dir, exist_ok=True)

    file_path = os.path.join(dir, file_name)

    with open(file_path, 'a') as json_file:
        json.dump(list(steps_per_food), json_file, indent=4)
        json_file.write("\n") 
    
    print(f"Steps data saved to {file_path}")

def export_num_foods_eaten(num):
    try:
        # Verifica se a entrada é um número inteiro
        if not isinstance(num, int):
            raise ValueError("A entrada deve ser um número inteiro.")
        
        # Caminho do arquivo
        file_path = os.path.join("data", "num_foods_eaten.txt")
        
        # Garante que a pasta 'data' existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Abre o arquivo no modo append (adicionar ao final) e escreve o número em uma nova linha
        with open(file_path, "a") as file:
            file.write(f"{num}\n")
        print(f"Número {num} adicionado ao ficheiro '{file_path}'.")
    except Exception as e:
        print(f"Erro ao escrever no ficheiro: {e}")

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
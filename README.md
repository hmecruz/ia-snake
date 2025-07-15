# ia-snakes
Snakes clone for AI teaching

## Project Description

The game is based on the traditional Snake game with some modifications. Details about these changes and the project requirements can be found in the IA_Snake.pdf file located in the root directory.

### AI Snake Game Agent

- Designed and implemented an AI agent for a customized version of the classic Snake game, achieving the highest score in the annual AI course competition at UA DETI.
- Integrated and adapted pathfinding algorithms such as Dijkstra, BFS, and A* to optimize gameplay strategies.

## How to Install

Make sure you are running Python 3.11.

```bash
$ python3 -m venv venv
$ source venv/bin/activate  # On Windows use `venv\Scripts\activate`
$ pip install -r requirements.txt
```

## How to Play

Open 3 terminals and run the following commands:

```bash
$ python3 server.py
$ python3 viewer.py
$ python3 student.py
```

`student.py` runs the AI agent code developed for the game.

To play using the sample client, make sure the client pygame hidden window has focus and run the following:

```bash
$ python3 server.py
$ python3 viewer.py
$ python3 client.py
```

## 🕹️ Playing on a Local Server with Multiple Agents

You can run the game locally and control multiple agents (snakes). Follow these steps:

1. **Start the server** (replace `x` with the number of players you want):

   ```bash
   python server.py --players x
   ```

   Example for 2 players:

   ```bash
   python server.py --players 2
   ```

2. **Run the game viewer** in another terminal:

   ```bash
   python viewer.py
   ```

3. **Start each agent (student bot)** in separate terminals.  
   Each player **must have a unique name**:

   ```bash
   NAME=player1 python student.py
   NAME=player2 python student.py
   ```

   ✅ You can use any name you like, as long as all player names are different.

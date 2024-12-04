#!/bin/bash


# if a error appears saying 'Permission denied' when trying to run the script, run this in the terminal: chmod +x run2.sh

# Caminho do diretório atual
DIR="$(cd "$(dirname "$0")" && pwd)"

# Comando para ativar o ambiente virtual
ACTIVATE_CMD="source venv/bin/activate"

# Abra o primeiro terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; python3 server.py --players 2" &
sleep 0.1

# Abra o segundo terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; python3 viewer.py" &
sleep 0.1

# Abra o terceiro terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; NAME='player1' python3 student.py" & 

# Abra o quarto terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; NAME='player2' python3 student.py" & 
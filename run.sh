#!/bin/bash

# Caminho do diretório atual
DIR="$(cd "$(dirname "$0")" && pwd)"

# Comando para ativar o ambiente virtual
ACTIVATE_CMD="source venv/bin/activate"

# Abra o primeiro terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; python3 server.py" &
sleep 0.1

# Abra o segundo terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; python3 viewer.py" &
sleep 0.1

# Abra o terceiro terminal em modo "fullscreen"
xterm -geometry 1800x1012 -hold -e "cd $DIR; $ACTIVATE_CMD; python3 student.py -out filename.json" & # Change the file name when executing
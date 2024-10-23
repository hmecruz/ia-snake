# Run on the root project directory

.PHONY: run

run:
	python3 student.py

run_server:
	SERVER=sokoban.av.it.pt PORT=80 NAME=dgomes python3 student.py
import json
import os
import sys
import inspect


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from maze_generators.algorthms import depth_first
from maze_generators.renderer.simple import simple_outline
from maze_generators.maze.maze import Maze

index = 0
for i in range(5,21):
    for _ in range(4):
        index += 1
        maze = depth_first.generate(i, i)

        name ="grid_{index:02}.json"

        maze.to_file(name)
        with open("jsons/" + name) as f:
            maze = Maze.from_json(json.loads(f.read()))

        renderer = simple_outline(maze, width=500, height=500, loops_skip=True)
        with open(f"output/grid/{index:02}_simple.svg", "w") as svg_file:
            svg_file.write(renderer)
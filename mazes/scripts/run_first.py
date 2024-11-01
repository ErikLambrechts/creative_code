
import sys
sys.path.append("..")

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from maze_generators.algorthms import recursive_devision
from maze_generators.algorthms import depth_first

from maze_generators.renderer.simple import simple_outline, simple_path



# maze = recursive_devision.generate(14,14)
maze = depth_first.generate(20,20)
print(str(maze))
maze.to_file("rdm.json")

import json
from maze_generators.renderer.path import path
from maze_generators.renderer.debug_renderer import debug_render
from maze_generators.maze.base import Maze


with open("jsons/rdm.json") as f:
    maze = Maze.from_json(json.loads(f.read()))

renderer = debug_render(maze, width=500, height=500)
with open(f"output/AA_debug_tmp.svg", "w") as svg_file:
    svg_file.write(renderer)

renderer = simple_outline(maze, width=500, height=500, loops_skip=True)
with open(f"output/AA_simple_outline.svg", "w") as svg_file:
    svg_file.write(renderer)
    
# renderer = simple_path(maze_recursive_division, width=500, height=500)
# with open(f"output/simple_path.svg", "w") as svg_file:
#     svg_file.write(renderer)

# renderer = path(maze_recursive_division, width=500, height=500)
# with open(f"output/path.svg", "w") as svg_file:
#     svg_file.write(renderer)
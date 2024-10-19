

from maze_generators.recursive_devision import generate_recursive_division_maze
from maze_generators.renderer.simple import simple_outline, simple_path



maze_recursive_division = generate_recursive_division_maze(14,14)
print(str(maze_recursive_division))
maze_recursive_division.to_file("rdm.json")

import json
from maze_generators.renderer.path import path
from maze_generators.renderer.debug_renderer import debug_render
from maze_generators.maze.base import Maze


with open("jsons/rdm.json") as f:
    maze_recursive_division = Maze.from_json(json.loads(f.read()))

# renderer = debug_render(maze_recursive_division, width=500, height=500)
# with open(f"output/debug_tmp.svg", "w") as svg_file:
#     svg_file.write(renderer)

renderer = simple_outline(maze_recursive_division, width=500, height=500, loops_skip=True)
with open(f"output/simple_outline.svg", "w") as svg_file:
    svg_file.write(renderer)
    
# renderer = simple_path(maze_recursive_division, width=500, height=500)
# with open(f"output/simple_path.svg", "w") as svg_file:
#     svg_file.write(renderer)

# renderer = path(maze_recursive_division, width=500, height=500)
# with open(f"output/path.svg", "w") as svg_file:
#     svg_file.write(renderer)
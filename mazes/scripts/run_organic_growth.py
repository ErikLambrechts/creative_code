import sys

import numpy as np
from shapely import Polygon

sys.path.append("..")

import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from maze_generators.maze.organic_growth_maze import OrganicGrowthMaze as OGMaze
import json
from maze_generators.renderer.debug_renderer import debug_render_maze


# Define the torus shape using two concentric circles (outer and inner boundary)
def create_torus(inner_radius, outer_radius, resolution=100):
    theta = np.linspace(0, 2 * np.pi, resolution)
    outer_circle = [(outer_radius * np.cos(t), outer_radius * np.sin(t)) for t in theta]
    inner_circle = [(inner_radius * np.cos(t), inner_radius * np.sin(t)) for t in theta]
    return Polygon(outer_circle + inner_circle[::-1])


torus_polygon = create_torus(inner_radius=0.5, outer_radius=1.5)
nr_points = 40
fixed_points = {0: (-1.5, 0), nr_points - 1: (1.5, 0)}
maze = OGMaze(
    nr_points=nr_points, fixed_points=fixed_points, boundary_polygon=torus_polygon
)

maze.min_distance = 0.10
maze.k_repulsion = 5

maze.simulate(num_iterations=1200, dt=0.12)

maze.to_file("rdm.json")

with open("jsons/rdm.json") as f:
    maze = OGMaze.from_json(json.loads(f.read()))

renderer = debug_render_maze(maze, width=500, height=500)
with open(f"output/OGMaze.svg", "w") as svg_file:
    svg_file.write(renderer)

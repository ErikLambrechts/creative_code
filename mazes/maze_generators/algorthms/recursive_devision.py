import json
import random

from ..maze.base import RectangularMaze as Maze

def generate_recursive_division_maze(width, height, maze=None, offset_x=0, offset_y=0):
    

    print("=====")

    r = random.randint(0, width + height - 3)
    print("offset_x:", offset_x, "  offset_y:", offset_y)
    print("width:", width, "  height:", height)


    if r < height - 1:
        opening = random.randint(0, width-1 ) + offset_x
        r_ = r
        r += offset_y
        for i in range(offset_x, width+offset_x):
            if i != opening:
                edge = (
                    maze[i, r],
                    maze[i, r+1]
                )
                maze.graph.remove(edge)
        if r_ >= 1:
            generate_recursive_division_maze(width, r_ + 1, maze, offset_x, offset_y)
        if height - r_ > 2:
            generate_recursive_division_maze(width, height - r_ -  1, maze, offset_x, offset_y + r_+1)
    else:
        r -= height - 1
        
        # r += 1
        r_ = r
        r += offset_x
        
        opening = random.randint(0, height-1 )+ offset_y
        for i in range(offset_y, height+offset_y):
            if i != opening:
                edge = (
                    maze[r, i],
                    maze[r+1, i]
                )
                maze.graph.remove(edge)
                
        if r_ >= 1 :
            generate_recursive_division_maze(r_+1, height, maze, offset_x, offset_y)
        if width - r_ > 2:
            generate_recursive_division_maze(width - r_ - 1, height, maze, offset_x+r_+1, offset_y)
        
    return maze

def generate(width, height):
    maze = Maze(width, height)
    maze.fill_graph()
    generate_recursive_division_maze(height, width, maze, 0, 0)
    return maze
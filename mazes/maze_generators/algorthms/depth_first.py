import json
import random

from ..maze.base import RectangularMaze as Maze

import numpy as np
import matplotlib.pyplot as plt
import random




class DepthFirst:
    def __init__(self, maze):
        self.maze = maze
        self.reset()

    def reset(self):
        self.possible_edges = self.maze.possible_edges()
        self.visited = np.zeros(self.maze.nr_nodes, dtype=bool)

    def random_start(self):
        return random.randint(0, self.maze.nr_nodes-1)

    def generate(self, node):
        # print(str(self.maze))
        # print(self.maze.graph)
        """Recursive DFS maze generation."""
        self.visited[node] = 1  # Mark as a path
        
        next_nodes = self.possblle_next_point(node)
        random.shuffle(next_nodes)  # Randomize direction for more randomness
        
        print(next_nodes)
        for next_node in next_nodes:
            next_node = int(next_node)
            if self.is_valid(next_node):
                self.maze.graph.append(( node, next_node ))
                self.generate(next_node)  # Recursive DFS call

    def possblle_next_point(self, node):
        """Check if the cell is within bounds and not visited yet."""
        # print(node)
        return np.argwhere(self.possible_edges[node] == 1).flatten()

    def is_valid(self, node):
        return not self.visited[node]


def generate(width, height):
    maze = Maze(width, height)

    df = DepthFirst(maze)
    node = df.random_start()
    m = df.generate(node)

    print(str(maze))
    print(maze.graph)
    return maze


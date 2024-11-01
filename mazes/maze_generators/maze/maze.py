from abc import abstractmethod
import json

import numpy as np

class Maze:
    def __init__(self, nodes=None, connections=None, vertices=None, faces=None):
        self.name = "Indexed Maze"
        self.nodes = nodes
        self.connections = connections


    @property
    def nr_nodes(self):
        return len(self.nodes)

    def to_json(self):
        if isinstance(self.nodes, np.ndarray):
            self.nodes = self.nodes.tolist()
        d = {
            "class": self.__class__.__name__,
            "name": self.name,
            "nodes": self.nodes,
            "connections": self.connections,
        }
        return json.dumps(d, indent=2)

    @staticmethod
    def from_json(json_string):
        json_string["class"]

        if json_string["class"] == "RectangularMaze":
            from .rectangular_maze import RectangularMaze
            maze = RectangularMaze(
                json_string["nr_col"],
                json_string["nr_row"],
            )
            maze.connections = json_string["connections"],
        else:
            maze = Maze(
                json_string["nodes"],
                json_string["connections"],
            )

        return maze

    def to_file(self, filename):
        with open(f"jsons/"+filename, "w") as f:
            f.write(self.to_json())

    def contains_connection(self, edge):
        edge = (edge[0], edge[1])
        edge_reversed = (edge[1], edge[0])
        return (edge in self.connections) or (edge_reversed in self.connections)
    
    @abstractmethod
    def possible_edges(self):
        pass
        
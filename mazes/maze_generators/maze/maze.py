from abc import abstractmethod
from dataclasses import dataclass, field
import json
from typing import List, Optional

import numpy as np
class Maze:
    def __init__(self, nodes=None, graph=None, vertices=None, faces=None):
        self.name = "Indexed Maze"
        self.nodes = nodes
        self.graph = graph


    @property
    def nr_nodes(self):
        return len(self.nodes)

    def to_json(self):
        d = {
            "class": self.__class__.__name__,
            "name": self.name,
            "nodes": self.nodes,
            "graph": self.graph,
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
            maze.graph = json_string["graph"]
        else:
            maze = Maze(
                json_string["nodes"],
                json_string["graph"],
            )

        return maze

    def to_file(self, filename):
        with open(f"jsons/"+filename, "w") as f:
            f.write(self.to_json())

    def graph_contains_edge(self, edge):
        edge = (edge[0], edge[1])
        edge_reversed = (edge[1], edge[0])
        return (edge in self.graph) or (edge_reversed in self.graph)
    


    @abstractmethod
    def possible_edges(self):
        pass
        
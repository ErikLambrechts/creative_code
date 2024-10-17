from dataclasses import dataclass, field
import json
from typing import List, Optional

import numpy as np

@dataclass 
class Vertex:
    coordinates: np.ndarray
    maze: 'Maze' = None

    index: int = field(init=False)

    def to_json(self):
        return  self.coordinates.tolist() 

    def __post_init__(self):
        self.maze.vertices.append(self)
        self.index = len(self.maze.vertices)-1
        
    def __getitem__(self, index):
        return self.coordinates[index]

    @property
    def x(self):
        return self.coordinates[0]
    
    @property
    def y(self):
        return self.coordinates[1]


@dataclass
class Face:
    vertex_indices: list[int]
    maze: 'Maze' = None
    
    index: int = field(init=False)
    loops: List['Loop'] = field(init=False)

    def __post_init__(self):
        self.maze.faces.append(self)
        self.index = len(self.maze.faces)-1
        self.loops = []
        for i in range(len(self.vertex_indices)):
            start = self.vertex_indices[i]
            end = self.vertex_indices[(i+1) % len(self.vertex_indices)]
            
            self.loops.append(Loop(start, end, self, self.maze))


    def to_json(self):
        return self.vertex_indices

    def contains_loop(self, loop):
        return loop in self.loops
    

@dataclass
class Loop:
    vertex_index: int
    vertex_next_index: int
    face: 'Face'
    # edge: Edge                 # The edge this loop is part of
    maze: 'Maze' = None  # Reference to the parent Maze, set by the update method

    @property
    def next_loop(self):
        return self.face.loops[(self.face.loops.index(self)+1) % len(self.face.loops)]

    @property
    def prev_loop(self):
        return self.face.loops[(self.face.loops.index(self)-1) % len(self.face.loops)]
    
    @property
    def opposite_loop(self):
        reversed_loop = Loop(self.vertex_next_index, self.vertex_index, None, self.maze)
        for f in self.maze.faces:
            if f.contains_loop(reversed_loop):
                reversed_loop.face = f
                return reversed_loop
        return None

    def __eq__(self, loop):
        return self.vertex_index == loop.vertex_index and self.vertex_next_index == loop.vertex_next_index
        
    def is_open(self) -> bool:
        """Check if this loop is open by verifying the connection between its face's centroid and the opposite loop's face centroid."""
        if self.opposite_loop is None:
            return False  # If there is no opposite loop, it's not an open connection.
        
        current_centroid_index = self.face.index
        opposite_centroid_index = self.opposite_loop.face.index
        
        # Check if the tuple (current_centroid, opposite_centroid) or (opposite_centroid, current_centroid) is in the graph
        return  ( [ current_centroid_index, opposite_centroid_index ] in self.maze.graph or \
               [ opposite_centroid_index, current_centroid_index ] in self.maze.graph)

    @property
    def coor(self):
        return self.maze.vertices[self.vertex_index]

class Maze:
    def __init__(self, centroids=None, graph=None, vertices=None, faces=None):
        self.name = "Indexed Maze"
        self.centroids = centroids
        self.graph = graph
        if vertices == None:
            vertices = []
        self.vertices = vertices
        if faces == None:
            faces = []
        self.faces = faces

    def to_json(self):
        d = {
            "name": self.name,
            "centroids": self.centroids,
            "graph": self.graph,
            "vertices": [v.to_json() for v in self.vertices],
            "faces": [f.to_json() for f in self.faces]
        }
        return json.dumps(d, indent=2)

    @staticmethod
    def from_json(json_string):
        maze = Maze(
            json_string["centroids"],
            json_string["graph"],
        )

        for v in json_string["vertices"]:
            maze.new_vertex(*v) 
        for f in json_string["faces"]:
            maze.new_face(f) 

        return maze

    def to_file(self, filename):
        with open("jsons/"+filename, "w") as f:
            f.write(self.to_json())
        
    def bounding_box(self):
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for x,y in self.vertices:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
        return min_x, min_y, max_x, max_y

    def new_vertex(self, x, y):
        return Vertex(np.array([x,y]), self)
    
    def new_face(self, vertices):
        return Face(vertices, self)


    def graph_contains_edge(self, edge):
        edge_reversed = (edge[1], edge[0])
        return (list(edge) in self.graph) or (list(edge_reversed) in self.graph)
    
        

class RectangularMaze(Maze):
    def __init__(self, nr_col, nr_row):
        self.nr_col = nr_col
        self.nr_row = nr_row

        centroids = []
        for y in range(nr_row):
            for x in range(nr_col):
                centroids.append([x,y])

        graph = []
        vertices = []
        faces = []

        super().__init__(centroids, graph, vertices, faces)

    def fill(self):
        self.graph = [
            (i, i+1) for i in range(self.nr_col*self.nr_row-1) if (i+1) % self.nr_col != 0
        ]

        for i in range(self.nr_col*self.nr_row-self.nr_col):
            self.graph.append((i, i+self.nr_col))


        for y in range(self.nr_row + 1):
            for x in range(self.nr_col + 1):
                self.new_vertex(x - 0.5,y - 0.5)

        for y in range(self.nr_row):
            for x in range(self.nr_col):
                self.new_face( [y*(self.nr_col+1)+x, y*(self.nr_col+1)+x+1, (y+1)*(self.nr_col+1)+x+1, (y+1)*(self.nr_col+1)+x])
        

    def __getitem__(self, pos):
        x,y = pos
        return y*self.nr_col+x

    def __str__(self):
        s = ""
        w = self.nr_col
        h = self.nr_row
        for y in range(h).__reversed__():
            s += '   '
            for x in range(w):
                s += '+'
                if (self[x,y], self[x+1,y]) in self.graph:
                    s += '--'
                else:
                    s += '  '
            s += '\n'
            if y == 0:
                break
            s += f'{y-1:2d} '
            for x in range(w):
                if (self[x,y-1], self[x,y]) in self.graph:
                    s += '|'
                else:
                    s += ' '
                s += '  '
            s += '\n'

        s += '   '
        for x in range(w-1):
            s += f' {x:2d}'
        s+= "\nnr_col: {} nr_row: {}".format(self.nr_col, self.nr_row)

        return s
    


from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass 
class Vertex:
    coordinates: np.ndarray
    maze: 'Maze' = None # type: ignore

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
    maze: 'Maze' = None # type: ignore
    
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
    maze: 'Maze' = None  # type: ignore # Reference to the parent Maze, set by the update method

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

class MazeMesh:
    def __init__(self, maze, vertices, graph, faces):
        self.maze = maze
        self.init_mesh(vertices, faces)

    def init_mesh(self, vertices, faces):
        self.vertices = []
        self.faces = []
        for v in vertices:
            self.new_vertex(v[0], v[1])

        for f in faces:
            self.new_face(f) 

    def to_json(self):
        vertices = [v.to_json() for v in self.vertices]
        faces = [f.to_json() for f in self.faces]
        return {"vertices": vertices, "faces": faces}

    def to_file(self, filename):
        with open(f"jsons/"+filename, "w") as f:
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

        edge = (edge[0], edge[1])
        edge_reversed = (edge[1], edge[0])
        return (edge in self.graph) or (edge_reversed in self.graph)
    

    def possible_edges(self):
        pass
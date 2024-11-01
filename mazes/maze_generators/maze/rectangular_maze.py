


import numpy as np
from .maze_mesh import MazeMesh
from .base import Maze


class RectangularMaze(Maze):
    def __init__(self, nr_col, nr_row):
        self.nr_col = nr_col
        self.nr_row = nr_row

        nodes = []
        for y in range(nr_row):
            for x in range(nr_col):
                nodes.append([x,y])

        graph = []
        super().__init__(nodes, graph)
        self.init_mesh()


    @property
    def shape(self):
        return self.nr_row, self.nr_col

    def fill_graph(self):
        self.graph = [
            (i, i+1) for i in range(self.nr_col*self.nr_row-1) if (i+1) % self.nr_col != 0
        ]

        for i in range(self.nr_col*self.nr_row-self.nr_col):
            self.graph.append((i, i+self.nr_col))

    def to_maze_mesh(self):
        verts = []
        for y in range(self.nr_row + 1):
            for x in range(self.nr_col + 1):
                verts.append((x - 0.5,y - 0.5))

        faces = []
        for y in range(self.nr_row):
            for x in range(self.nr_col):
                faces.append( [y*(self.nr_col+1)+x, y*(self.nr_col+1)+x+1, (y+1)*(self.nr_col+1)+x+1, (y+1)*(self.nr_col+1)+x])
        
        return MazeMesh(self, verts, faces)

    
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
                if self[x,y] < 10:
                    s+= str(self[x,y])
                else:
                    s += '+'
                if self.graph_contains_edge((self[x,y], self[x+1,y])):
                    s += '--'
                else:
                    s += '  '
            s += '\n'
            if y == 0:
                break
            s += f'{y-1:2d} '
            for x in range(w):
                if self.graph_contains_edge((self[x,y], self[x+1,y])):
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
    
    def possible_edges(self):
        possiblle_edges = np.zeros((self.nr_col*self.nr_row, self.nr_col*self.nr_row), dtype=bool)
        width = self.nr_col
        height = self.nr_row
        for x in range(0, width):
            for y in range(0, height):
                
                if x < width - 1:
                    possiblle_edges[self[x,y], self[x+1,y]] = 1
                if y < height - 1:
                    possiblle_edges[self[x,y], self[x,y+1]] = 1
                    

        possiblle_edges = possiblle_edges + possiblle_edges.T
        return possiblle_edges
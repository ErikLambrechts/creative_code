import json
import sys
from matplotlib.lines import Line2D

sys.path.append("..")
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from maze_generators.maze.organic_growth_maze import OrganicGrowthMaze as OGMaze
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, Delaunay
import numpy as np
from shapely.geometry import Polygon, LineString
import shapely.geometry

class Maze:
    def __init__(self, nodes, connections, contour):
        """
        Initialize the Maze with nodes, connections, and contour.
        
        Parameters:
        - nodes: List of tuples, where each tuple is a (x, y) point representing a node.
        - connections: List of tuples, where each tuple is (node_index1, node_index2),
                       representing an edge between the two nodes.
        - contour: A shapely.geometry.Polygon object representing the boundary of the maze,
                   possibly with holes.
        """
        self.nodes = np.array(nodes)
        self.connections = connections
        self.contour = contour
        self.voronoi = None
        self.delaunay = None

    def compute_bounded_voronoi(self):
        """Compute a bounded Voronoi diagram by adding points around the bounding box of the contour."""
        # Step 1: Get bounding box of the contour
        minx, miny, maxx, maxy = self.contour.bounds
        
        # Step 2: Add extra points to create a bounding box for the Voronoi diagram
        padding = max(maxx - minx, maxy - miny) 
        bbox_points = [
            (minx - padding, miny - padding),
            (minx - padding, maxy + padding),
            (maxx + padding, miny - padding),
            (maxx + padding, maxy + padding)
        ]
        
        # Step 3: Combine original nodes with bounding box points
        all_points = np.vstack([self.nodes, bbox_points])
        
        # Step 4: Compute the Voronoi diagram with these points
        self.voronoi = Voronoi(all_points)
    
    def compute_edges(self):
        self.edges = []

        for edge_index, ridge in enumerate(self.voronoi.ridge_vertices):
            if -1 not in ridge:  # Skip edges extending to infinity
                regions = self.voronoi.ridge_points[ edge_index ]
                print(f"Edge {edge_index} separates regions {regions[0]} and {regions[1]}")

                if  ( [int(regions[0]),int(regions[1])] in self.connections) or ([ int(regions[1]),int(regions[0]) ] in self.connections ):
                    print("skip")
                    continue

                line = LineString([self.voronoi.vertices[ridge[0]], self.voronoi.vertices[ridge[1]]])
                line_clipped = line.intersection(self.contour)
                if line_clipped.is_empty:
                    continue
                if line_clipped.geom_type == 'MultiLineString':
                    for line in line_clipped.geoms:
                        self.edges.append(line)
                elif line_clipped.geom_type == 'LineString':
                    self.edges.append(line_clipped)
                
        print(len(self.edges))

        
        
    def compute_clip_voronoi(self):
        # Step 5: Clip each Voronoi region with the contour polygon
        self.voronoi_regions_clipped = []
        for region_index in self.voronoi.point_region[:len(self.nodes)]:
            region = self.voronoi.regions[region_index]
            if not region or -1 in region:
                continue  # Skip regions that still extend to infinity (unlikely with bbox)

            # Get the vertices of the Voronoi region polygon
            region_points = [self.voronoi.vertices[i] for i in region]
            region_polygon = Polygon(region_points)
            
            # Intersect with the contour
            clipped_region = region_polygon.intersection(self.contour)
            if not clipped_region.is_empty:
                self.voronoi_regions_clipped.append(clipped_region)

    def compute_delaunay(self):
        """Compute the Delaunay triangulation for the nodes."""
        self.delaunay = Delaunay(self.nodes)

    def draw(self):
        """
        Draw the maze with nodes, connections, bounded Voronoi diagram, and Delaunay triangulation.
        """
        # Ensure bounded Voronoi and Delaunay structures are computed
        self.compute_bounded_voronoi()
        self.compute_clip_voronoi()
        self.compute_edges()
        self.compute_delaunay()

        # Plot nodes as blue dots
        # for node in self.nodes:
        #     plt.plot(node[0], node[1], 'bo')  # 'bo' is a blue dot

        # # Plot connections as black lines
        # for connection in self.connections:
        #     x1, y1 = self.nodes[connection[0]]
        #     x2, y2 = self.nodes[connection[1]]
        #     plt.plot([x1, x2], [y1, y2], 'k-')  # 'k-' is a black line

        # Plot the contour
        # x, y = self.contour.exterior.xy
        # plt.plot(x, y, 'g-', linewidth=2)  # Green outline for contour
        # for hole in self.contour.interiors:
        #     hx, hy = hole.xy
        #     plt.plot(hx, hy, 'g-')  # Dashed green line for holes

        # # Plot bounded and clipped Voronoi regions
        # for clipped_region in self.voronoi_regions_clipped:
        #     if clipped_region.geom_type == 'GeometryCollection':
        #         for geom in clipped_region.geoms:
        #             if geom.geom_type == 'Polygon':
        #                 self.draw_clipped_polygon(geom)
        #             else:
        #                 print(geom.geom_type)

        #         continue


        #     self.draw_clipped_polygon(clipped_region)

        # Plot Delaunay triangles
        # for simplex in self.delaunay.simplices:
        #     plt.plot(self.nodes[simplex, 0], self.nodes[simplex, 1], 'r--')  # Dashed red line for Delaunay edges
        #     plt.plot(self.nodes[simplex[np.array([-1,0])], 0], self.nodes[simplex[np.array([-1,0])], 1], 'r--')

        # # Highlight connections in Delaunay and their dual edges in Voronoi
        # for connection in self.connections:
        #     if set(connection) in [set(edge) for edge in self.delaunay.simplices]:
        #         # Highlight the Delaunay edge as a thicker blue line
        #         x1, y1 = self.nodes[connection[0]]
        #         x2, y2 = self.nodes[connection[1]]
        #         plt.plot([x1, x2], [y1, y2], 'b-', linewidth=2)

        #         # Highlight the dual Voronoi edge if it exists
        #         voronoi_edge = self.get_dual_edge(connection)
        #         if voronoi_edge is not None:
        #             vx1, vy1 = voronoi_edge[0]
        #             vx2, vy2 = voronoi_edge[1]
        #             plt.plot([vx1, vx2], [vy1, vy2], 'c-', linewidth=2)  # Cyan for dual Voronoi edge


        # for edge in self.edges:
        #     x, y = edge.xy
        #     plt.plot(x, y, 'r-', linewidth=2)

        a = shapely.union_all(self.edges)
        a = a.buffer(0.001)
        # a = a.simplify(tolerance=0.01)

        if False:
            a = self.contour.difference(a)
            a = a.buffer(-0.04)
            a = a.buffer(0.03)
            a = a.buffer(-0.02)

        else:
            a = self.contour.intersection(a)
            a = self.contour.boundary.buffer(0.001).union(a)
            a = a.buffer(0.04)
            a = a.buffer(-0.03)
            a = a.buffer(0.02)


        if a.geom_type == 'Polygon':
            x, y = a.exterior.xy
            plt.plot(x, y, 'r-', linewidth=2)
            for interior in a.interiors:
                ix, iy = interior.xy
                plt.plot(ix, iy, 'r', linewidth=2)
        else:
            
            for p in a.geoms:
                x, y = p.exterior.xy
                plt.plot(x, y, 'r-', linewidth=2)
                for interior in p.interiors:
                    ix, iy = interior.xy
                    plt.plot(ix, iy, 'r', linewidth=2)
        # legend_elements = [
        #     Line2D([0], [0], color='blue', marker='o', label='Nodes', linestyle='None'),
        #     Line2D([0], [0], color='black', label='Connections'),
        #     Line2D([0], [0], color='green', linewidth=2, label='Contour'),
        #     Line2D([0], [0], color='orange', linewidth=1, label='Voronoi Regions'),
        #     Line2D([0], [0], color='red', linestyle='--', label='Delaunay Triangles'),
        #     Line2D([0], [0], color='blue', linewidth=2, label='Highlighted Connection'),
        #     Line2D([0], [0], color='cyan', linewidth=2, label='Dual Voronoi Edge')
        # ]

        

        # plt.legend(handles=legend_elements, loc='upper right')
        plt.gca().set_aspect('equal', adjustable='box')
        # Set aspect ratio and show the plot
        plt.show()

    def draw_clipped_polygon(self, clipped_region):
        x, y = clipped_region.exterior.xy
        for interior in clipped_region.interiors:
            ix, iy = interior.xy
            plt.plot(ix, iy, 'orange', linewidth=1)
                
        plt.fill(x, y, edgecolor='orange', fill=False, linewidth=1)
            # Plot any holes within Voronoi regions
        for interior in clipped_region.interiors:
            ix, iy = interior.xy
            plt.plot(ix, iy, 'orange', linewidth=1)

    def get_dual_edge(self, connection):
        """
        Get the dual Voronoi edge for a given Delaunay edge (connection).
        
        Parameters:
        - connection: A tuple (node_index1, node_index2)
        
        Returns:
        - A tuple with two points (each point being (x, y)) representing the Voronoi edge, or None if not found.
        """
        point_index1, point_index2 = connection
        ridge_points = list(zip(self.voronoi.ridge_points, self.voronoi.ridge_vertices))
        
        # Find the Voronoi edge that corresponds to this Delaunay edge
        for (p1, p2), (v1, v2) in ridge_points:
            if {point_index1, point_index2} == {p1, p2} and v1 != -1 and v2 != -1:
                return (self.voronoi.vertices[v1], self.voronoi.vertices[v2])
        
        return None

def create_torus(inner_radius, outer_radius, resolution=100):
    theta = np.linspace(0, 2 * np.pi, resolution)
    outer_circle = [(outer_radius * np.cos(t), outer_radius * np.sin(t)) for t in theta]
    inner_circle = [(inner_radius * np.cos(t), inner_radius * np.sin(t)) for t in theta]
    return Polygon(outer_circle + inner_circle[::-1])


torus_polygon = create_torus(inner_radius=0.4, outer_radius=1.5)
# Example usage:
nodes = [(0.3, 0), (1, 1), (1, 0.1), (0, 1), (2.5, 2)]
connections = [(0, 1), (1, 2), (2, 3), (1, 4)]

with open("mazes/jsons/rdm.json") as f:
    maze = OGMaze.from_json(json.loads(f.read()))

nodes = maze.nodes
connections = maze.connections 

# Define a contour polygon with an outer boundary and a hole
outer_boundary = [(-1, -1), (3, -1), (3, 3), (-1, 3), (-1, -1)]
hole = [(1.5, 0.5), (1.5, 1.5), (2.5, 1.5), (2.5, 0.5), (1.5, 0.5)]
contour = Polygon(shell=outer_boundary, holes=[hole])
# contour = Polygon(shell=outer_boundary)

contour = torus_polygon.buffer(0.2)
maze = Maze(nodes, connections, contour)
maze.draw()

from itertools import combinations
import json
import math
import shapely
from shapely import affinity
from shapely.plotting import plot_polygon, plot_points
from matplotlib import pyplot as plt
import numpy as np
from shapely import LineString, MultiLineString, Point, line_merge, unary_union, ops

import textwrap
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


from maze_generators.maze.organic_growth_maze import OrganicGrowthMaze as OGMaze

class Graph:
    def __init__(self):
        self.points = []  # List of 2D points, e.g., [(x1, y1), (x2, y2), ...]
        self.edges = []   # List of edges as tuples of point indices, e.g., [(0, 1), (1, 2), ...]
        self.d = 0.045

    def add_point(self, point):
        """Add a point to the graph and return its index."""
        self.points.append(point)
        return len(self.points) - 1

    def add_edge(self, index1, index2):
        """Add an edge between two points by their indices."""
        self.edges.append((index1, index2))

    def edge_length(self, index1, index2):
        """Calculate the Euclidean distance between two points given their indices."""
        x1, y1 = self.points[index1]
        x2, y2 = self.points[index2]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def subdivide_edge(self, index1, index2, threshold):
        """Subdivide a long edge by adding intermediate points if it exceeds the threshold."""
        length = self.edge_length(index1, index2)
        if length <= threshold:
            # If the edge is within the threshold, keep it as it is
            return [(index1, index2)]

        # Calculate the number of segments needed to keep each new edge within the threshold
        num_segments = math.ceil(length / threshold)
        new_edges = []

        # Retrieve the coordinates of the original points
        x1, y1 = self.points[index1]
        x2, y2 = self.points[index2]

        # Interpolate points along the edge
        prev_index = index1
        for i in range(1, num_segments):
            # Calculate the interpolated point
            t = i / num_segments
            new_x = x1 + t * (x2 - x1)
            new_y = y1 + t * (y2 - y1)

            # Add the new point and create a new edge
            new_index = self.add_point((new_x, new_y))
            new_edges.append((prev_index, new_index))
            prev_index = new_index

        # Add the final edge to connect the last new point to the second original point
        new_edges.append((prev_index, index2))
        return new_edges

    def enforce_edge_threshold(self, threshold):
        """Modify the graph so that no edge exceeds the given length threshold."""
        new_edges = []
        for index1, index2 in self.edges:
            # Subdivide the edge if necessary and collect the resulting edges
            new_edges.extend(self.subdivide_edge(index1, index2, threshold))
        
        # Replace the original edges with the new set of edges
        self.edges = new_edges

    def neighbors(self, point_index):
        """Get all neighbors of a point based on the edges."""
        return [j for i, j in self.edges if i == point_index] + [i for i, j in self.edges if j == point_index]

    def buffer_graph(self, edges):
        points = self.points
        if isinstance(edges, int):
            shape = Point(points[edges])
        else:
            shapely_edges = [LineString([points[e[0]], points[e[1]]]) for e in edges]
            shape = unary_union(shapely_edges)
        # TODO use offset curve
        return shape.buffer(self.d)

    def plot_sub(self, ax, sub_graph_edges):
        """Calculate the area of a polygon given by a list of point indices using the Shoelace formula."""
        
        buffer = self.buffer_graph(sub_graph_edges)

        col = (np.random.random(), np.random.random(), np.random.random())

        plot_polygon(buffer, ax=ax, add_points=False, color=col)

    def sub_graph_hole_free(self, sub_graph_edges):
        """Calculate the area of a polygon given by a list of point indices using the Shoelace formula."""
        
        buffer = self.buffer_graph(sub_graph_edges)

        return len(buffer.interiors) == 0

    def divide_graph(self):
        """Divide the graph into subgraphs where each subgraph's area is below a certain threshold."""
        visited = set()
        subgraphs = []

        remaining_points = list(range(len(self.points)))
        remaining_edges = self.edges.copy()

        start_bridge = []

        sub_graph_buffer_total = None


        while remaining_edges:
            possible_starts = []
            
            # start_point = random.choice(remaining_points)
            if len(start_bridge) > 0:
                start_point = start_bridge.pop()[0]
                bridge = True
            else:
                start_point = remaining_points[0]
                bridge = False
            subgraph_points = [start_point]
            subgraph_edges = []
            stack = [start_point]
            # visited.add(start_point)

                

            while stack:
                current_point = stack.pop()
                remaining_points.remove(current_point)
                for neighbor in self.neighbors(current_point):
                    if not edge_in_edge_list((current_point, neighbor), remaining_edges):
                        continue
                    # Temporarily add the neighbor to the subgraph and check the area
                    tmp_edges = subgraph_edges + [[current_point, neighbor]]
                        
                    if bridge:
                        landing_bridge = self.buffer_graph(current_point)
                        landing_free = shapely.disjoint(landing_bridge, sub_graph_buffer_total)
                        
                        if landing_free:
                            possible_starts.append(current_point)
                            remaining_points.append(current_point)
                            
                        else:
                            subgraph_points.append(neighbor)
                            subgraph_edges.append((current_point, neighbor))
                            stack.append(neighbor)
                            visited.add(neighbor)
                            remaining_edges = [e for e in remaining_edges if e != (current_point, neighbor) and e != (neighbor, current_point)]
                    else:
                        if self.sub_graph_hole_free(tmp_edges):
                            # Safe to add neighbor without exceeding area threshold
                            subgraph_points.append(neighbor)
                            subgraph_edges.append((current_point, neighbor))
                            stack.append(neighbor)
                            visited.add(neighbor)
                            remaining_edges = [e for e in remaining_edges if e != (current_point, neighbor) and e != (neighbor, current_point)]
                        else:
                            # Area limit exceeded; mark this point as a new start
                            possible_starts.append(current_point)
                            remaining_points.append(current_point)
                            start_bridge.append((current_point, neighbor))

                count_neighbors_in_same_sub_graph = sum([1 for n in self.neighbors(current_point) if edge_in_edge_list((n, current_point), subgraph_edges)])
                if count_neighbors_in_same_sub_graph < len(self.neighbors(current_point)):
                    possible_starts.append(current_point)
            if len(subgraph_points) == 1:
                continue

            # Save the current subgraph
            subgraphs.append({
                "points": subgraph_points,
                "edges": subgraph_edges,
                "connections": list(set(possible_starts)),
                "bridge": bridge,
            })

            sub_graph_buffer = self.buffer_graph(subgraph_edges)
            if sub_graph_buffer_total is None:
                sub_graph_buffer_total = sub_graph_buffer
            else:
                sub_graph_buffer = shapely.union(sub_graph_buffer, sub_graph_buffer_total)

        return subgraphs

    def pairwise_bisectors(self, node):
        def calculate_angle(origin, point):
            """Calculate the angle from origin to point relative to the x-axis in radians."""
            dx, dy = point[0] - origin[0], point[1] - origin[1]
            return math.atan2(dy, dx)

        """
        For each consecutive clockwise pair of neighbors, calculate the bisector direction.
        Handles collinear pairs using orthogonal vectors.
        """
        
        neighbors_ind = self.neighbors(node)
        point = self.points[node]

        # Calculate angles of each neighbor relative to the point
        neighbors_with_angles = [
            (self.points[index], calculate_angle(point, self.points[index]), index) for index in neighbors_ind
        ]
        
        # Sort neighbors in clockwise order based on angles
        neighbors_with_angles.sort(key=lambda x: x[1])
        
        # Prepare the result list
        bisectors = []
        
        # Go through each consecutive pair in the clockwise order
        num_neighbors = len(neighbors_with_angles)
        for i in range(num_neighbors):
            # Define consecutive neighbors in a circular fashion
            neighbor1 = neighbors_with_angles[i]
            neighbor2 = neighbors_with_angles[(i + 1) % num_neighbors]
            

            neighbor1_point, neighbor1_angle, neighbor1_index = neighbor1
            neighbor2_point, neighbor2_angle, neighbor2_index = neighbor2

            if neighbor1_angle > neighbor2_angle:
                neighbor2_angle += 2 * math.pi
            angle = (neighbor2_angle + neighbor1_angle) / 2
            bisectors.append({
                "direction": (math.cos(angle), math.sin(angle)),
                "neighbors": (neighbor1_index, neighbor2_index),
            })
        
        return bisectors


def normalize(vector):
    """Normalize a 2D vector."""
    x, y = vector
    magnitude = math.sqrt(x ** 2 + y ** 2)
    return (x / magnitude, y / magnitude) if magnitude != 0 else (0, 0)

def edge_in_edge_list(edge, edge_list):
    """Check if an edge is already in the list of edges."""
    return edge in edge_list or (edge[1], edge[0]) in edge_list

def visualize_graph(graph, edges=None):
    if edges is None:
        edges  = graph.edges
    points = graph.points
    
    plt.figure(figsize=(8, 8))

    col = (np.random.random(), np.random.random(), np.random.random())
    # Plot the edges
    for p1, p2 in edges:
        plt.plot(
            [points[p1][0], points[p2][0]],
            [points[p1][1], points[p2][1]],
            color=col,
            linestyle="--",
        )

    # Plot the points
    for idx, point in enumerate(points):
        plt.plot(point[0], point[1], "bo")
        plt.text(point[0], point[1], f"{idx}", fontsize=12, ha="right")

    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.title("")
    plt.grid(True)
    plt.axis("equal")

def get_first_intersection(polygon, point, direction, ray_length=1e6):
    """
    Find the first intersection of a ray with a polygon.

    Parameters:
    - polygon: A Shapely Polygon object
    - point: A tuple (x, y) representing the starting point of the ray
    - direction: A tuple (dx, dy) representing the direction of the ray
    - ray_length: The length of the ray, should be large enough to ensure it intersects

    Returns:
    - The first intersection point as a Shapely Point, or None if no intersection
    """

    # Define the starting point of the ray
    start_point = Point(point)

    # Normalize the direction to unit length
    direction_length = math.sqrt(direction[0]**2 + direction[1]**2)
    direction = (direction[0] / direction_length, direction[1] / direction_length)

    # Define the end point of the ray using the normalized direction and a large length
    end_point = Point(
        start_point.x + direction[0] * ray_length,
        start_point.y + direction[1] * ray_length
    )

    # Create a line (ray) from the start point to the end point
    ray = LineString([start_point, end_point])

    # Compute the intersection of the ray and the polygon
    if polygon.area == 0:
        pass
    else:
        polygon = shapely.boundary(polygon)
    intersection = ray.intersection(polygon)

    # If there is no intersection, return None
    if intersection.is_empty:
        return None

    # If the intersection is a single point, return it
    if isinstance(intersection, Point):
        return intersection

    # If the intersection is a line (or contains multiple points),
    # find the first point along the ray direction
    if intersection.geom_type == "MultiPoint" or intersection.geom_type == "GeometryCollection":
        # Find the point closest to the start point
        
        closest_point = min(list(intersection.geoms), key=lambda p: start_point.distance(p))
        return closest_point

    return None


# Example usage:
graph = Graph()


points = [
    [0, 0],
    [1, 0],
    [1, 2],
    [0, 2],
    [0, 1],
    [2, 1],
    [3, 0],
    [3, 1.5],
    [-1, 2.5],
    [0, 2.5],
    [3, 3],
]

edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [4, 5],
    [5, 6],
    [5, 7],
    [8, 7],
    [10, 6],
    [10, 0],
]

# points = [
#     [0, 0],
#     [1, 0],
#     [1, 1],
#     [0, 1],
# ]

# edges = [
#     [0, 1],
#     [1, 2],
#     [2, 3],
# ]

with open("jsons/rdm.json") as f:
    maze = OGMaze.from_json(json.loads(f.read()))

points = maze.nodes
edges = maze.connections

for point in points:
    graph.add_point(point)
    
for edge in edges:
    graph.add_edge(*edge) 
    

# Set a threshold for edge length
threshold = .1

# Enforce the threshold
# graph.enforce_edge_threshold(threshold)

subgraphs = graph.divide_graph()

visualize_graph(graph)
fig, axis = plt.subplots(figsize=(8, 8))

# subgraphs = [
#     {"points":[0,1,2,3], "edges":[[0,1]], "connections":[1]},
#     {"points":[0,1,2,3], "edges":[[1,2]], "connections":[1,2]},
#     {"points":[0,1,2,3], "edges":[[2,3]], "connections":[2]},
# ]


for index_sub_graph, subgraph in enumerate(subgraphs):
    
    print(f"==========={index_sub_graph = }")
    # plt.grid(True)
    plt.axis("equal")
    graph.plot_sub(sub_graph_edges=subgraph["edges"], ax=axis)
    shape = graph.buffer_graph(subgraph["edges"])
    bourder_parts = [shape.boundary]
    first_cut = True
    print(f"{subgraph['edges'] = }")
    for idx, node in enumerate(subgraph["connections"]):
        
        print(f"======conections========={node = }")
        point = graph.points[node]
        axis.plot(point[0], point[1], "ro")
        axis.text(point[0], point[1], f"p_{idx}", fontsize=12, ha="right")

        bisectors = graph.pairwise_bisectors(node)
        for bisector in bisectors:
            print(f"-------bisectior---------{bisector = }")
            x = point[0] + bisector["direction"][0]
            y = point[1] + bisector["direction"][1]
            # axis.plot([point[0], x], [point[1], y], "g-")


            intersection = get_first_intersection(shape, point, bisector["direction"])
            
            if intersection:
                axis.scatter(intersection.x, intersection.y, color="red")
                axis.text(intersection.x, intersection.y, f"inter_{index_sub_graph}", fontsize=12)
                x = point[0] + 1.001*(intersection.x - point[0])
                y = point[1] + 1.001*(intersection.y - point[1])
                intersection = LineString([point, (x,y)])

                new_bourders = [] 
                for part in bourder_parts:
                    print(f"    part = ")
                    intersection_part = get_first_intersection(part, point, bisector["direction"])
                    if not intersection_part:
                        print("no intersection")
                        new_bourders.append(part)
                        continue
                    if intersection_part.distance(intersection) > 1e-6:
                        print("intesection not on bourder", intersection_part.distance(intersection), intersection_part, intersection)
                        new_bourders.append(part)
                        continue
                    
                    print("iteresection", intersection_part)
                    parts = part.difference(intersection_part.buffer(1e-13))
                    if parts.geom_type == "LineString":
                        new_bourders.append(parts)
                    else:
                        for s in  parts.geoms :
                            new_bourders.append(s)

                if len(new_bourders) == len(bourder_parts):
                    print("no split")
                    first_cut = False
                bourder_parts = new_bourders
        
        if first_cut:
            first_cut = False
            f = bourder_parts.pop(0)
            l = bourder_parts.pop(-1)
            n = line_merge(MultiLineString([l, f]))
            bourder_parts = [n] + bourder_parts
    
        print(f"bourders: {len(bourder_parts)}")
            

        bourder_parts = sorted(bourder_parts, key=lambda x: x.centroid.distance(Point(point)), reverse=False)
        bourder_parts = bourder_parts[1:]
            

    subgraph["buffer"] = shape
    subgraph["contours"] = bourder_parts

    for idx, p in enumerate(bourder_parts):
        col = (np.random.random(), np.random.random(), np.random.random())
        axis.plot(*p.xy, color=col, linewidth=4)

    pass

    # TODO check if neighbors are in the same subgraph only when more than 2 neighbors
        
        

fig, ax = plt.subplots(figsize=(8, 8))

plt.axis("equal")
contours = []


subgraphs_bridge = [subgraph for subgraph in subgraphs if subgraph["bridge"]]
subgraphs_not_bridege = [subgraph for subgraph in subgraphs if not subgraph["bridge"]]

for sub_graph in subgraphs:
    contours_new = []
    for contour in contours:
        diff = shapely.difference(contour, sub_graph["buffer"])
        if diff.geom_type == "MultiLineString":
            contours_new.extend(list(diff.geoms))
        else:
            contours_new.append(diff)
            
    contours_new.extend( sub_graph["contours"] )
    contours = contours_new
    print(sub_graph["bridge"])

for contour in contours:
    col = (np.random.random(), np.random.random(), np.random.random())
    ax.plot(*contour.xy, color=col, linewidth=4)

contours = [c for c in contours if c.is_empty == False]
area = MultiLineString(contours)

area = affinity.scale(area, xfact=200, yfact=200)
with open('test_OGM_03.svg', 'w') as f:
    #specify margin in coordinate units
    margin = 5

    bbox = list(area.bounds)
    bbox[0] -= margin
    bbox[1] -= margin
    bbox[2] += margin
    bbox[3] += margin

    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    #transform each coordinate unit into "scale" pixels
    scale = 10

    props = {
        'version': '1.1',
        'baseProfile': 'full',
        'width': '{width:.0f}px'.format(width = width*scale),
        'height': '{height:.0f}px'.format(height = height*scale),
        'viewBox': '%.1f,%.1f,%.1f,%.1f' % (bbox[0], bbox[1], width, height),
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:ev': 'http://www.w3.org/2001/xml-events',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink'
    }

    f.write(textwrap.dedent(r'''
        <?xml version="1.0" encoding="utf-8" ?>
        <svg {attrs:s}>
        {data:s}
        </svg>
    ''').format(
        attrs = ' '.join(['{key:s}="{val:s}"'.format(key = key, val = props[key]) for key in props]),
        data = area.svg()
    ).strip())

plt.show()
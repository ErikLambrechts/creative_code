
import numpy as np

# Scale vertices and centroids to fit the SVG canvas
def scale_point(maze, point: np.ndarray, width: int, height: int, padding: int = 50):
    """Scale a point (np.array) to fit within the SVG canvas."""
    max_x, max_y = np.max([v.coordinates for v in maze.vertices], axis=0)
    min_x, min_y = np.min([v.coordinates for v in maze.vertices], axis=0)
    scale_x = (width - 2 * padding) / (max_x - min_x)
    scale_y = (height - 2 * padding) / (max_y - min_y)
    scaled_x = (point[0] - min_x) * scale_x + padding
    scaled_y = (point[1] - min_y) * scale_y + padding
    return scaled_x, scaled_y

def simple_path(maze: 'Maze', width: int = 500, height: int = 500) -> str:
    """Generate an SVG representation of the maze for debugging purposes."""
    # SVG header
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           f'width="{width}" height="{height}">']
    
    # Define some styling
    svg.append('''
        <style>
            .vertex { fill: blue; stroke: none; }
            .edge { stroke: black; stroke-width: 2; }
            .loop { stroke: black; stroke-width: 2; }
            .face { fill: none; stroke: red; stroke-width: 1; }
            .centroid { fill: green; }
            .graph-edge { stroke: green; stroke-width: 3;  }
            .loop-arrow { fill: none; stroke: purple; stroke-width: 1; }
            .label { font-size: 12px; fill: black; }
        </style>
    ''')


    # Step 1: Render all vertices
    for i, vertex in enumerate(maze.vertices):
        x, y = scale_point(maze, vertex.coordinates, width, height)
        svg.append(f'<circle class="vertex" cx="{x}" cy="{y}" r="5"/>')
        svg.append(f'<text class="label" x="{x + 8}" y="{y + 5}">V{i}</text>')  # Label the vertex

    # # Step 2: Render all edges
    # for edge in maze.edges:
    #     v1 = maze.vertices[edge.start_vertex]
    #     v2 = maze.vertices[edge.end_vertex]
    #     x1, y1 = scale_point(v1.coordinates, width, height)
    #     x2, y2 = scale_point(v2.coordinates, width, height)
    #     svg.append(f'<line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    # Step 3: Render all faces as polygons
    for face in maze.faces:
        points = []
        for v_index in face.vertex_indices:
            v = maze.vertices[v_index]
            x, y = scale_point(maze, v.coordinates, width, height)
            points.append(f'{x},{y}')
        points_str = " ".join(points)
        svg.append(f'<polygon class="face" points="{points_str}"/>')

    # Step 4: Render all centroids
    for i, centroid in enumerate(maze.centroids):
        x, y = scale_point(maze, centroid, width, height)
        svg.append(f'<rect class="centroid" x="{x - 5}" y="{y - 5}" width="10" height="10"/>')
        svg.append(f'<text class="label" x="{x + 8}" y="{y + 5}">C{i}</text>')  # Label the centroid

    # Step 5: Render the graph edges (centroid connections)
    for start_idx, end_idx in maze.graph:
        start_centroid = maze.centroids[start_idx]
        end_centroid = maze.centroids[end_idx]
        x1, y1 = scale_point(maze, start_centroid, width, height)
        x2, y2 = scale_point(maze, end_centroid, width, height)
        svg.append(f'<line class="graph-edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    # Optional Step 6: Render loop directions (if needed)
    # for loop in maze.loops:
    #     v1 = maze.vertices[loop.vertex_indices[0]]
    #     v2 = maze.vertices[loop.vertex_indices[1]]
    #     x1, y1 = scale_point(v1.coordinates, width, height)
    #     x2, y2 = scale_point(v2.coordinates, width, height)

    #     # Draw an arrow to show the direction of the loop
    #     mid_x = (x1 + x2) / 2
    #     mid_y = (y1 + y2) / 2
    #     svg.append(f'<line class="loop-arrow" x1="{mid_x}" y1="{mid_y}" x2="{x2}" y2="{y2}"/>')
    #     svg.append(f'<polygon class="loop-arrow" points="{x2},{y2} {x2-3},{y2-3} {x2+3},{y2-3}"/>')

    # SVG footer
    svg.append('</svg>')
    
    return "\n".join(svg)


def simple_outline(maze: 'Maze', width: int = 500, height: int = 500, loops_skip=None) -> str:

    if loops_skip is None:
        loops_skip = []
        
    if loops_skip == True:
        loops_skip = [
            maze.faces[0].loops[0],
            maze.faces[-1].loops[-2]
        ]
    """Generate an SVG representation of the maze for debugging purposes."""
    # SVG header
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           f'width="{width}" height="{height}">']
    
    # Define some styling
    svg.append('''
        <style>
            .edge { stroke: black; stroke-width: 2; }
        </style>
    ''')

    for face in maze.faces:
        for loop in face.loops:
            if loop in loops_skip:
                continue
            if  loop.is_open():
                continue
            v1 = loop.coor
            v2 = loop.next_loop.coor
            x1, y1 = scale_point(maze, v1.coordinates, width, height)
            x2, y2 = scale_point(maze, v2.coordinates, width, height)

            svg.append(f'<line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    # SVG footer
    svg.append('</svg>')
    
    return "\n".join(svg)

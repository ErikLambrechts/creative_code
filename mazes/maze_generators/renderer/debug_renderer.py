import numpy as np


def debug_render_maze(maze: 'Maze', width: int = 500, height: int = 500) -> str:
    """Generate an SVG representation of the maze for debugging purposes."""
    # SVG header
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           f'width="{width}" height="{height}">']
    
    # Define some styling
    svg.append('''
        <style>
            .vertex { fill: blue; stroke: none; }
            .edge { stroke: black; stroke-width: 2; }
            .face { fill: none; stroke: red; stroke-width: 1; }
            .centroid { fill: green; }
            .graph-edge { stroke: green; stroke-width: 3;  }
            .loop-arrow { fill: none; stroke: purple; stroke-width: 1; }
            .label { font-size: 12px; fill: black; }
        </style>
    ''')

    # Scale vertices and centroids to fit the SVG canvas
    def scale_point(point: np.ndarray, width: int, height: int, padding: int = 50):
        """Scale a point (np.array) to fit within the SVG canvas."""
        max_x = np.max([v[0] for v in maze.nodes], axis=0)
        max_y = np.max([v[1] for v in maze.nodes], axis=0)
        min_x = np.min([v[0] for v in maze.nodes], axis=0)
        min_y = np.min([v[1] for v in maze.nodes], axis=0)
        scale_x = (width - 2 * padding) / (max_x - min_x)
        scale_y = (height - 2 * padding) / (max_y - min_y)
        scaled_x = (point[0] - min_x) * scale_x + padding
        scaled_y = (point[1] - min_y) * scale_y + padding
        return scaled_x, scaled_y

    # # Step 1: Render all vertices
    # for i, vertex in enumerate(maze.vertices):
    #     x, y = scale_point(vertex.coordinates, width, height)
    #     svg.append(f'<circle class="vertex" cx="{x}" cy="{y}" r="5"/>')
    #     svg.append(f'<text class="label" x="{x + 8}" y="{y + 5}">V{i}</text>')  # Label the vertex

    # # # Step 2: Render all edges
    # # for edge in maze.edges:
    # #     v1 = maze.vertices[edge.start_vertex]
    # #     v2 = maze.vertices[edge.end_vertex]
    # #     x1, y1 = scale_point(v1.coordinates, width, height)
    # #     x2, y2 = scale_point(v2.coordinates, width, height)
    # #     svg.append(f'<line class="edge" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    # # Step 3: Render all faces as polygons
    # for face in maze.faces:
    #     points = []
    #     for v_index in face.vertex_indices:
    #         v = maze.vertices[v_index]
    #         x, y = scale_point(v.coordinates, width, height)
    #         points.append(f'{x},{y}')
    #     points_str = " ".join(points)
    #     svg.append(f'<polygon class="face" points="{points_str}"/>')

    # Step 4: Render all centroids
    for i, node in enumerate(maze.nodes):
        x, y = scale_point(node, width, height)
        svg.append(f'<rect class="centroid" x="{x - 5}" y="{y - 5}" width="10" height="10"/>')
        svg.append(f'<text class="label" x="{x + 8}" y="{y + 5}">C{i}</text>')  # Label the centroid

    # Step 5: Render the graph edges (centroid connections)
    for start_idx, end_idx in maze.connections:
        start_centroid = maze.nodes[start_idx]
        end_centroid = maze.nodes[end_idx]
        x1, y1 = scale_point(start_centroid, width, height)
        x2, y2 = scale_point(end_centroid, width, height)
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

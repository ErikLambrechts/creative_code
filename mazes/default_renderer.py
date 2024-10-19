import numpy as np

from maze.maze import Maze


import svgwrite
from svgwrite.shapes import Line

class MazeRenderer:
    @staticmethod
    def default_renderer2(maze: 'Maze', wall_thickness: float = 10, offset: float = 5) -> svgwrite.Drawing:
        """
        Renders the maze, drawing only the open edges between centroids (based on the maze graph).
        The wall thickness adds a visual separation to represent walls of the maze.
        :param maze: The Maze object to render.
        :param wall_thickness: The thickness of the walls in the maze.
        :param offset: Offset to create a separation between the paths and walls.
        :return: An SVG drawing of the maze.
        """
        # Create an SVG canvas
        min_x, min_y, max_x, max_y = maze.bounding_box()
        drawing = svgwrite.Drawing(size=(int((max_x - min_x)*100), int((max_y - min_y)*100)))

        # Define styles for the walls and open paths
        wall_style = {"stroke": "black", "stroke-width": wall_thickness, "stroke-linecap": "round"}
        path_style = {"stroke": "white", "stroke-width": wall_thickness - offset, "stroke-linecap": "round"}

        # Draw open edges (connections between centroids)
        for edge in maze.edges:
            if  edge.is_open():  # Only draw open edges
                start_vertex = maze.vertices[edge.start_vertex]
                end_vertex = maze.vertices[edge.end_vertex]


                print(start_vertex[0] * 100, start_vertex[1] * 100)
                # Draw the wall (background) as a thick black line
                drawing.add(Line(
                    start=(float(start_vertex[0] * 100), float(start_vertex[1] * 100)),
                    end=(float(end_vertex[0] * 100), float(end_vertex[1] * 100)),
                    **wall_style
                ))

                # Draw the open path as a thinner white line on top
                drawing.add(drawing.line(
                    start=(float(start_vertex[0] * 100), float(start_vertex[1] * 100)),
                    end=(float(end_vertex[0] * 100), float(end_vertex[1] * 100)),
                    **path_style
                ))

        return drawing


def default_render(maze: Maze, width: int = 500, height: int = 500, wall_thickness: float = 5.0) -> str:
    """Generate an SVG representation of the maze with wall thickness for solving."""
    # SVG header
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
           f'width="{width}" height="{height}">']

    # Define some styling
    svg.append('''
        <style>
            .wall { fill: black; stroke: none; }
            .background { fill: white; }
        </style>
    ''')

    # Scale vertices and centroids to fit the SVG canvas
    def scale_point(point: np.ndarray, width: int, height: int, padding: int = 50):
        """Scale a point (np.array) to fit within the SVG canvas."""
        max_x, max_y = np.max([v.coordinates for v in maze.vertices], axis=0)
        min_x, min_y = np.min([v.coordinates for v in maze.vertices], axis=0)
        scale_x = (width - 2 * padding) / (max_x - min_x)
        scale_y = (height - 2 * padding) / (max_y - min_y)
        scaled_x = (point[0] - min_x) * scale_x + padding
        scaled_y = (point[1] - min_y) * scale_y + padding
        return scaled_x, scaled_y

    # Utility to get perpendicular offset points for thickening the edges
    def offset_edge(v1: np.ndarray, v2: np.ndarray, thickness: float):
        """Given two points, return the four corner points of a thickened wall along the edge."""
        direction = v2 - v1
        length = np.linalg.norm(direction)
        if length == 0:
            return []
        
        # Normal vector for the edge (perpendicular direction)
        normal = np.array([-direction[1], direction[0]]) / length
        offset = normal * (thickness / 2)

        # Return the four corners of the thickened wall
        p1 = v1 + offset
        p2 = v1 - offset
        p3 = v2 - offset
        p4 = v2 + offset
        return [p1, p2, p3, p4]

    # Step 1: Render background
    svg.append(f'<rect class="background" x="0" y="0" width="{width}" height="{height}"/>')

    # Step 2: Render all edges as thick walls
    for edge in maze.edges:
        v1 = maze.vertices[edge.start_vertex]
        v2 = maze.vertices[edge.end_vertex]
        p1 = scale_point(v1.coordinates, width, height)
        p2 = scale_point(v2.coordinates, width, height)

        # Compute the offset rectangle (wall) for this edge
        corners = offset_edge(np.array(p1), np.array(p2), wall_thickness)
        if corners:
            points_str = " ".join(f'{x},{y}' for x, y in corners)
            svg.append(f'<polygon class="wall" points="{points_str}"/>')

    # SVG footer
    svg.append('</svg>')

    return "\n".join(svg)

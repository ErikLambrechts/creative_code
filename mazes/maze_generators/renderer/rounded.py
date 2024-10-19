
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

def simple_line(maze: 'Maze', width: int = 500, height: int = 500) -> str:
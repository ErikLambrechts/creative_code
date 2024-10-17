import numpy as np
import shapely
from shapely.geometry import Polygon, LineString
from shapely.ops import linemerge, unary_union, polygonize
        
        

import geopandas as gpd
import matplotlib.pyplot as plt
            
            

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

def path(maze: 'Maze', width: int = 500, height: int = 500) -> str:
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
            .graph-edge { stroke: black; stroke-width: 6;  }
            .loop-arrow { fill: none; stroke: purple; stroke-width: 1; }
            .label { font-size: 12px; fill: black; }
        </style>
    ''')

    patches = []
    
    for f in maze.faces:
        vertex_coords = [scale_point(maze,l.coor,width,height) for l in f.loops]

        polygon = Polygon(vertex_coords)
        parts = []
        
        for index, loop in enumerate(f.loops):
            if not loop.is_open():
                continue
            vertex_coords_shift = vertex_coords[index:] + vertex_coords[:index]
            outer_edge = shapely.LineString(vertex_coords_shift) .buffer(5, single_sided=True)
            parts.append(polygon.difference(outer_edge))
                
        print(len(parts))
        new_polygon = shapely.union_all(parts)

        # myPoly = gpd.GeoSeries([new_polygon])
        # myPoly.plot()
        # plt.show()        
                
        svg.append(new_polygon.svg())
            
        patches.append(new_polygon)

    # SVG footer
    svg.append('</svg>')
    
    return "\n".join(svg)
import svgwrite
from svgwrite import cm, mm
import random
from scipy.spatial import Voronoi, Delaunay
import numpy as np
import math

# Constants
A3_WIDTH = 297  # mm
A3_HEIGHT = 420  # mm
GRID_COLS = 5  # 5 columns
GRID_ROWS = 7  # 7 rows
CELL_WIDTH = A3_WIDTH / GRID_COLS
CELL_HEIGHT = A3_HEIGHT / GRID_ROWS
BORDER_PADDING = 5  # Padding within each cell

# Initialize SVG canvas
dwg = svgwrite.Drawing('grid_patterns.svg', profile='full', size=(A3_WIDTH * mm, A3_HEIGHT * mm))

# Utility functions for patterns
def solid_color_pattern(color):
    return dwg.rect(size=("100%", "100%"), fill=color)

def stripes_pattern(angle, color1, color2, stripe_width=5):
    pattern = dwg.pattern(id=f"stripes_{angle}", size=(stripe_width, stripe_width), patternUnits="userSpaceOnUse")
    pattern.add(dwg.rect(size=(stripe_width, stripe_width), fill=color1))
    pattern.add(dwg.line(start=(0, 0), end=(stripe_width, stripe_width), stroke=color2, stroke_width=2))
    return pattern

def checkered_pattern(color1, color2, square_size=10):
    pattern = dwg.pattern(id="checkered", size=(square_size * 2, square_size * 2), patternUnits="userSpaceOnUse")
    pattern.add(dwg.rect(insert=(0, 0), size=(square_size, square_size), fill=color1))
    pattern.add(dwg.rect(insert=(square_size, square_size), size=(square_size, square_size), fill=color1))
    pattern.add(dwg.rect(insert=(square_size, 0), size=(square_size, square_size), fill=color2))
    pattern.add(dwg.rect(insert=(0, square_size), size=(square_size, square_size), fill=color2))
    return pattern

def polka_dots_pattern(color1, color2, radius=3, spacing=10):
    pattern = dwg.pattern(id="polka_dots", size=(spacing, spacing), patternUnits="userSpaceOnUse")
    pattern.add(dwg.circle(center=(spacing/2, spacing/2), r=radius, fill=color1, stroke=color2))
    return pattern

def concentric_circles_pattern(color1, color2):
    pattern = dwg.pattern(id="concentric_circles", size=(20, 20), patternUnits="userSpaceOnUse")
    for r in range(5, 15, 5):
        pattern.add(dwg.circle(center=(10, 10), r=r, fill="none", stroke=color1 if r % 2 == 0 else color2))
    return pattern

def wavy_lines_pattern(color):
    path = dwg.path(d="M 0 10 Q 5 0, 10 10 T 20 10", stroke=color, fill="none", stroke_width=2)
    return path

def zigzag_pattern(color):
    path = dwg.polyline(points=[(0, 5), (5, 0), (10, 5), (15, 0), (20, 5)], stroke=color, fill="none", stroke_width=2)
    return path

def spirals_pattern(color):
    path = dwg.path(d="M 10,10 Q 15,15, 20,10 T 30,10", stroke=color, fill="none", stroke_width=2)
    return path

def hexagonal_tiling_pattern(color1, color2):
    pattern = dwg.pattern(id="hexagonal_tiling", size=(20, 20), patternUnits="userSpaceOnUse")
    for i in range(0, 40, 20):
        for j in range(0, 40, 20):
            points = [(i + 10, j), (i + 20, j + 10), (i + 10, j + 20), (i, j + 10)]
            pattern.add(dwg.polygon(points=points, fill=color1 if (i + j) % 40 == 0 else color2))
    return pattern

def starburst_pattern(color):
    pattern = dwg.pattern(id="starburst", size=(20, 20), patternUnits="userSpaceOnUse")
    for i in range(0, 20, 5):
        pattern.add(dwg.line(start=(10, 10), end=(i, 0), stroke=color, stroke_width=1))
        pattern.add(dwg.line(start=(10, 10), end=(20, i), stroke=color, stroke_width=1))
    return pattern

def maze_pattern(color):
    pattern = dwg.pattern(id="maze", size=(20, 20), patternUnits="userSpaceOnUse")
    pattern.add(dwg.line(start=(0, 0), end=(10, 10), stroke=color, stroke_width=1))
    pattern.add(dwg.line(start=(10, 0), end=(20, 10), stroke=color, stroke_width=1))
    pattern.add(dwg.line(start=(0, 10), end=(10, 20), stroke=color, stroke_width=1))
    pattern.add(dwg.line(start=(10, 10), end=(20, 20), stroke=color, stroke_width=1))
    return pattern


# Function to draw a square with a specific pattern
def draw_square(x, y, fill_pattern):
    dwg.add(dwg.rect(insert=(x, y), size=(CELL_WIDTH - BORDER_PADDING, CELL_HEIGHT - BORDER_PADDING), fill=fill_pattern, stroke="black", stroke_width=1))

def escher_tessellation_pattern():
    pattern = dwg.pattern(id="escher_tessellation", size=(20, 20), patternUnits="userSpaceOnUse")
    # Create interlocking shapes (simplified)
    pattern.add(dwg.polygon(points=[(0, 0), (10, 0), (10, 10), (0, 10)], fill="blue"))
    pattern.add(dwg.polygon(points=[(10, 10), (20, 10), (20, 20), (10, 20)], fill="yellow"))
    return pattern

def fractal_tree_pattern():
    pattern = dwg.pattern(id="fractal_tree", size=(20, 20), patternUnits="userSpaceOnUse")
    # Recursive branching (simplified)
    pattern.add(dwg.line(start=(10, 10), end=(15, 5), stroke="green", stroke_width=2))
    pattern.add(dwg.line(start=(15, 5), end=(20, 0), stroke="green", stroke_width=1))
    return pattern

def optical_illusion_pattern():
    pattern = dwg.pattern(id="optical_illusion", size=(20, 20), patternUnits="userSpaceOnUse")
    # Penrose triangle or impossible shape (simplified)
    pattern.add(dwg.path(d="M 0,0 L 10,0 L 5,15 Z", fill="none", stroke="black", stroke_width=2))
    return pattern

def circuit_board_pattern():
    pattern = dwg.pattern(id="circuit_board", size=(20, 20), patternUnits="userSpaceOnUse")
    # Circuit-like pattern
    pattern.add(dwg.rect(insert=(5, 5), size=(10, 10), fill="none", stroke="blue"))
    pattern.add(dwg.line(start=(0, 5), end=(10, 5), stroke="blue", stroke_width=1))
    pattern.add(dwg.circle(center=(10, 10), r=2, fill="blue"))
    return pattern

def dynamic_flow_pattern():
    pattern = dwg.pattern(id="dynamic_flow", size=(20, 20), patternUnits="userSpaceOnUse")
    # Flowing wave-like pattern
    pattern.add(dwg.path(d="M 0,10 C 5,5 15,15 20,10", stroke="purple", fill="none", stroke_width=1))
    return pattern



# Function to generate a Voronoi Diagram Pattern
def voronoi_pattern():
    points = np.random.rand(10, 2) * 20  # 10 random points within 20x20 grid
    vor = Voronoi(points)
    pattern = dwg.pattern(id="voronoi", size=(20, 20), patternUnits="userSpaceOnUse")
    
    for region in vor.regions:
        if not -1 in region and region:
            polygon = [vor.vertices[i] for i in region]
            pattern.add(dwg.polygon(points=polygon, fill=random.choice(["#FFB6C1", "#87CEEB", "#32CD32"])))
    return pattern

# Recursive function for a fractal pattern (like Sierpinski triangle)
def sierpinski_triangle(x, y, size, depth):
    if depth == 0:
        dwg.add(dwg.polygon(points=[(x, y), (x + size, y), (x + size / 2, y - size)], fill="none", stroke="black", stroke_width=0.5))
    else:
        half = size / 2
        sierpinski_triangle(x, y, half, depth - 1)
        sierpinski_triangle(x + half, y, half, depth - 1)
        sierpinski_triangle(x + half / 2, y - half, half, depth - 1)

def fractal_pattern(color):
    pattern = dwg.pattern(id="fractal", size=(20, 20), patternUnits="userSpaceOnUse")
    for i in range(5):
        for j in range(5):
            pattern.add(dwg.circle(center=(i * 4 + 2, j * 4 + 2), r=2, fill="none", stroke=color))
    return pattern

def fractal_sierpinski_pattern():
    pattern = dwg.pattern(id="sierpinski", size=(20, 20), patternUnits="userSpaceOnUse")
    sierpinski_triangle(0, 20, 20, 4)  # Draw 4 levels of recursion
    return pattern

# Function to generate Lissajous curves (like spirograph)
def lissajous_pattern():
    pattern = dwg.pattern(id="lissajous", size=(20, 20), patternUnits="userSpaceOnUse")
    for t in np.linspace(0, 2 * np.pi, 100):
        x = 10 + 8 * np.sin(3 * t)
        y = 10 + 8 * np.sin(5 * t)
        pattern.add(dwg.circle(center=(x, y), r=0.5, fill="none", stroke="purple"))
    return pattern

# Function for Delaunay triangulation pattern
def delaunay_pattern():
    points = np.random.rand(10, 2) * 20  # 10 random points
    tri = Delaunay(points)
    pattern = dwg.pattern(id="delaunay", size=(20, 20), patternUnits="userSpaceOnUse")
    
    for simplex in tri.simplices:
        triangle = [(points[simplex[0], 0], points[simplex[0], 1]),
                    (points[simplex[1], 0], points[simplex[1], 1]),
                    (points[simplex[2], 0], points[simplex[2], 1])]
        pattern.add(dwg.polygon(points=triangle, fill=random.choice(["#FFD700", "#00FA9A", "#8A2BE2"])))
    return pattern

# Function to create hyperbolic tiling pattern (Poincaré Disk Model)
def poincare_disk_pattern():
    pattern = dwg.pattern(id="poincare", size=(20, 20), patternUnits="userSpaceOnUse")
    
    # Recursively tile inside a circle
    def tile_circle(x, y, r, depth):
        if depth == 0:
            pattern.add(dwg.circle(center=(x, y), r=r, fill="none", stroke="black", stroke_width=0.5))
        else:
            for angle in np.linspace(0, 2 * np.pi, 6):
                nx = x + r * np.cos(angle)
                ny = y + r * np.sin(angle)
                tile_circle(nx, ny, r / 2, depth - 1)
    
    tile_circle(10, 10, 9, 3)  # 3 levels of recursion
    return pattern

# Apply these highly intricate patterns in the final row
for col in range(5):
    x = col * CELL_WIDTH + BORDER_PADDING / 2
    y = 6 * CELL_HEIGHT + BORDER_PADDING / 2  # Last row (7th row)

    if col == 0:
        dwg.defs.add(voronoi_pattern())
        fill_pattern = "url(#voronoi)"
    elif col == 1:
        dwg.defs.add(fractal_sierpinski_pattern())
        fill_pattern = "url(#sierpinski)"
    elif col == 2:
        dwg.defs.add(lissajous_pattern())
        fill_pattern = "url(#lissajous)"
    elif col == 3:
        dwg.defs.add(delaunay_pattern())
        fill_pattern = "url(#delaunay)"
    elif col == 4:
        dwg.defs.add(poincare_disk_pattern())
        fill_pattern = "url(#poincare)"

    # Draw the square with the selected pattern
    draw_square(x, y, fill_pattern)

# Save the updated SVG
dwg.save()

# Fill each row with increasing complexity
for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        x = col * CELL_WIDTH + BORDER_PADDING / 2
        y = row * CELL_HEIGHT + BORDER_PADDING / 2
        
        if row == 0:
            # Simple patterns for first row
            if col == 0:
                fill_pattern = "red"
            elif col == 1:
                dwg.defs.add(stripes_pattern(45, "white", "black"))
                fill_pattern = "url(#stripes_45)"
            elif col == 2:
                dwg.defs.add(stripes_pattern(0, "white", "black"))
                fill_pattern = "url(#stripes_0)"
            elif col == 3:
                dwg.defs.add(stripes_pattern(90, "white", "black"))
                fill_pattern = "url(#stripes_90)"
            elif col == 4:
                dwg.defs.add(checkered_pattern("black", "white"))
                fill_pattern = "url(#checkered)"
        
        elif row == 1:
            # Slightly more complex patterns
            if col == 0:
                dwg.defs.add(polka_dots_pattern("black", "white"))
                fill_pattern = "url(#polka_dots)"
            elif col == 1:
                dwg.defs.add(stripes_pattern(45, "black", "white", 2))
                fill_pattern = "url(#stripes_45)"
            elif col == 2:
                dwg.defs.add(concentric_circles_pattern("black", "white"))
                fill_pattern = "url(#concentric_circles)"
            elif col == 3:
                dwg.defs.add(stripes_pattern(0, "black", "white", 2))
                fill_pattern = "url(#stripes_0)"
            elif col == 4:
                dwg.defs.add(stripes_pattern(90, "black", "white", 2))
                fill_pattern = "url(#stripes_90)"

        elif row == 2:
            # More advanced patterns
            if col == 0:
                draw_square(x, y, "blue")
                fill_pattern = "blue"
            elif col == 1:
                dwg.defs.add(zigzag_pattern("black"))
                fill_pattern = "url(#zigzag)"
            elif col == 2:
                dwg.defs.add(wavy_lines_pattern("black"))
                fill_pattern = "url(#wavy_lines)"
            elif col == 3:
                dwg.defs.add(stripes_pattern(45, "blue", "white", 3))
                fill_pattern = "url(#stripes_45)"
            elif col == 4:
                dwg.defs.add(concentric_circles_pattern("blue", "white"))
                fill_pattern = "url(#concentric_circles)"

        elif row == 3:
            # Even more advanced patterns
            if col == 0:
                dwg.defs.add(spirals_pattern("black"))
                fill_pattern = "url(#spirals)"
            elif col == 1:
                dwg.defs.add(checkered_pattern("black", "red", square_size=5))
                fill_pattern = "url(#checkered)"
            elif col == 2:
                dwg.defs.add(hexagonal_tiling_pattern("black", "white"))
                fill_pattern = "url(#hexagonal_tiling)"
            elif col == 3:
                dwg.defs.add(starburst_pattern("black"))
                fill_pattern = "url(#starburst)"
            elif col == 4:
                dwg.defs.add(maze_pattern("black"))
                fill_pattern = "url(#maze)"

        elif row == 4:
            # Highly intricate and imaginative patterns
            if col == 0:
                dwg.defs.add(fractal_pattern("black"))
                fill_pattern = "url(#fractal)"
            elif col == 1:
                dwg.defs.add(hexagonal_tiling_pattern("purple", "orange"))
                fill_pattern = "url(#hexagonal_tiling)"
            elif col == 2:
                # Abstract freeform shapes
                pattern = dwg.pattern(id="abstract_shapes", size=(20, 20), patternUnits="userSpaceOnUse")
                pattern.add(dwg.path(d="M 10,10 Q 20,5, 10,20 T 0,10", stroke="purple", fill="none"))
                dwg.defs.add(pattern)
                fill_pattern = "url(#abstract_shapes)"
            elif col == 3:
                # Detailed pattern mix (overlap of various patterns)
                pattern = dwg.pattern(id="pattern_mix", size=(20, 20), patternUnits="userSpaceOnUse")
                pattern.add(dwg.circle(center=(10, 10), r=5, fill="none", stroke="green"))
                pattern.add(dwg.line(start=(0, 0), end=(20, 20), stroke="blue", stroke_width=1))
                dwg.defs.add(pattern)
                fill_pattern = "url(#pattern_mix)"
            elif col == 4:
                # Complex, layered, abstract design
                pattern = dwg.pattern(id="complex_abstract", size=(20, 20), patternUnits="userSpaceOnUse")
                pattern.add(dwg.path(d="M 0,0 Q 10,20, 20,0 T 20,20", stroke="black", fill="none"))
                pattern.add(dwg.circle(center=(10, 10), r=8, fill="none", stroke="red"))
                pattern.add(dwg.line(start=(0, 10), end=(20, 10), stroke="orange", stroke_width=2))
                dwg.defs.add(pattern)
                fill_pattern = "url(#complex_abstract)"

        # Draw the square with the selected pattern
        draw_square(x, y, fill_pattern)

# Save the drawing
dwg.save()
# Add to the last row in the grid
for col in range(5):
    x = col * CELL_WIDTH + BORDER_PADDING / 2
    y = 6 * CELL_HEIGHT + BORDER_PADDING / 2  # Last row (7th row)

    if col == 0:
        dwg.defs.add(escher_tessellation_pattern())
        fill_pattern = "url(#escher_tessellation)"
    elif col == 1:
        dwg.defs.add(fractal_tree_pattern())
        fill_pattern = "url(#fractal_tree)"
    elif col == 2:
        dwg.defs.add(optical_illusion_pattern())
        fill_pattern = "url(#optical_illusion)"
    elif col == 3:
        dwg.defs.add(circuit_board_pattern())
        fill_pattern = "url(#circuit_board)"
    elif col == 4:
        dwg.defs.add(dynamic_flow_pattern())
        fill_pattern = "url(#dynamic_flow)"

    # Draw the square with the selected pattern
    draw_square(x, y, fill_pattern)

# Save the updated SVG
dwg.save()
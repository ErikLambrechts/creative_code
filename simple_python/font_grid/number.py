import svgwrite
from svgwrite import cm, mm

# Constants
A3_WIDTH = 297  # mm
A3_HEIGHT = 420  # mm
GRID_SIZE = 10  # 10x10 grid
CELL_WIDTH = A3_WIDTH / GRID_SIZE
CELL_HEIGHT = A3_HEIGHT / GRID_SIZE
BOLT_PADDING = 5  # Padding within each cell
FONT_SIZE = 25  # Font size for numbers
PATTERN_REPEAT_INTERVAL = 7  # Patterns repeat every 7 numbers
SCALE = 0.2
FONT = "Comic Sans MS"
FONT = "URW Bookman L"  
FONT = "Nimbus Mono PS Bold"


# Reinitialize SVG canvas with a full profile instead of 'tiny'
dwg = svgwrite.Drawing('number_grid.svg', profile='full', size=(A3_WIDTH, A3_HEIGHT))

# Create different patterns again
patterns = []

# Horizontal Stripes Pattern
stripe_pattern = dwg.pattern(id="horizontal_stripes", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
stripe_pattern.add(dwg.rect(insert=(0, 0), size=(10*SCALE, 5*SCALE), fill="black"))
patterns.append(stripe_pattern)

# Diagonal Stripes Pattern
diagonal_stripe = dwg.pattern(id="diagonal_stripes", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
diagonal_stripe.add(dwg.line(start=(0, 0), end=(10*SCALE, 10*SCALE), stroke="black", stroke_width=1))
diagonal_stripe.add(dwg.line(start=(10*SCALE, 0), end=(0, 10*SCALE), stroke="black", stroke_width=1))
patterns.append(diagonal_stripe)

# Grid Pattern
grid_pattern = dwg.pattern(id="grid_pattern", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
grid_pattern.add(dwg.line(start=(5*SCALE, 0), end=(5*SCALE, 10*SCALE), stroke="black", stroke_width=1))
grid_pattern.add(dwg.line(start=(0, 5*SCALE), end=(10*SCALE, 5*SCALE), stroke="black", stroke_width=1))
patterns.append(grid_pattern)

# Grid of Circles
circles_pattern = dwg.pattern(id="circle_grid", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
for x in range(2, 10, 5):
    for y in range(2, 10, 5):
        circles_pattern.add(dwg.circle(center=(x*SCALE, y*SCALE), r=1*SCALE, fill="black"))
patterns.append(circles_pattern)

# Triangles Pattern
triangle_pattern = dwg.pattern(id="triangle_grid", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
triangle_pattern.add(dwg.polygon(points=[(5*SCALE, 0), (10*SCALE, 10*SCALE), (0, 10*SCALE)], fill="black"))
patterns.append(triangle_pattern)

# Skewed Lines Pattern
skew_lines = dwg.pattern(id="skew_lines", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
skew_lines.add(dwg.line(start=(0, 0), end=(10*SCALE, 5*SCALE), stroke="black", stroke_width=1))
skew_lines.add(dwg.line(start=(0, 5*SCALE), end=(10*SCALE, 10*SCALE), stroke="black", stroke_width=1))
patterns.append(skew_lines)

# Zig-Zag Pattern
zigzag = dwg.pattern(id="zigzag", size=(10*SCALE, 10*SCALE), patternUnits="userSpaceOnUse")
zigzag.add(dwg.polyline(points=[(0, 5*SCALE), (2.5*SCALE, 2.5*SCALE), (5*SCALE, 5*SCALE), (7.5*SCALE, 7.5*SCALE), (10*SCALE, 5*SCALE)], stroke="black", fill="none", stroke_width=1))
patterns.append(zigzag)

# Add patterns to the canvas
for pattern in patterns:
    dwg.defs.add(pattern)

# Function to get the corresponding pattern
def get_pattern(number):
    pattern_index = (number - 1) % PATTERN_REPEAT_INTERVAL
    return patterns[pattern_index].get_funciri()

# Draw grid with numbers and patterns
for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        num = row * GRID_SIZE + col + 1
        x = col * CELL_WIDTH + BOLT_PADDING
        y = row * CELL_HEIGHT + BOLT_PADDING


        # Draw the number with the corresponding pattern
        text_x = x + (CELL_WIDTH - 2 * BOLT_PADDING) / 2
        text_y = y + (CELL_HEIGHT - 2 * BOLT_PADDING) / 2 + FONT_SIZE / 3
        # number = dwg.text(str(num), insert=(text_x, text_y), font_size=FONT_SIZE, font_family="Arial Rounded MT Bold",
        number = dwg.text(str(num), insert=(text_x, text_y), font_size=FONT_SIZE, font_family=FONT,
                          text_anchor="middle", alignment_baseline="middle", fill="none", stroke="black", stroke_width=1)
        number['fill'] = get_pattern(num)
        dwg.add(number)

# Save the drawing
dwg.save()
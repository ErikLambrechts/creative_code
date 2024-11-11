import textwrap
import xml.etree.ElementTree as ET
from shapely import LineString, LinearRing
import shapely
import copy
from shapely.geometry import Polygon
from svgpathtools import parse_path, Path
import numpy as np

from svgpathtools import Line, CubicBezier, QuadraticBezier, Arc

def parse_svg_for_paths(element, namespaces, path_elements=None, parent_transform=None, in_defs=False):
    """Recursively parses SVG elements, applies transformations, and collects paths."""
    if path_elements is None:
        path_elements = {}  # Initialize the cache for referenced paths by ID

    paths_to_draw = []

    if element.tag.endswith('defs'):
        in_defs = True
    # Combine current element's transformation with the parent transformation
    current_transform = element.attrib.get('transform')
    combined_transform = parent_transform if parent_transform is not None else np.identity(3)
    if current_transform:
        combined_transform = parse_transform(current_transform) @ combined_transform

    # Cache <path> elements by ID for later reference
    if element.tag.endswith('path') and 'id' in element.attrib:
        path_id = element.attrib['id']
        if path_id not in path_elements:
            path_elements[path_id] = parse_path(element.attrib['d'])  # Parse and store the path by ID

    # Check if the element is a direct <path> or a <use> referencing a path
    if element.tag.endswith('path') and 'd' in element.attrib and not in_defs:
        # Direct <path> element, parse and transform it
        path_data = element.attrib['d']
        path = parse_path(path_data)  # Assuming parse_path converts 'd' data to path segments
        transformed_path = apply_transform(path, combined_transform)
        paths_to_draw.append(transformed_path)

    elif element.tag.endswith('use'):
        # <use> element, fetch and transform the referenced path
        href = element.attrib.get('href', '').replace('#', '')
        if href in path_elements:
            # Apply the transformation to the referenced path if it's cached
            referenced_path = path_elements[href]
            transformed_path = apply_transform(referenced_path, combined_transform)
            paths_to_draw.append(transformed_path)

    # Recursively process all child elements
    for child in element:
        new_paths = parse_svg_for_paths(child, namespaces, path_elements, combined_transform, in_defs).copy()
        # if new_paths:
        #     print(new_paths[0][0].point(0))
        paths_to_draw.extend(new_paths)
        if paths_to_draw:
            print(element.tag)
            for path in paths_to_draw:
                print(path[0].point(0))

    return paths_to_draw.copy()

def parse_svg(svg_string):
    # Parse SVG XML structure
    root = ET.fromstring(svg_string)
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    
    # Find the viewBox and transformation matrix if present
    view_box = root.attrib.get('viewBox')
    transform = root.attrib.get('transform')

    
    parent_transform = np.identity(3)
    paths_to_draw = parse_svg_for_paths(root, ns, parent_transform=parent_transform)
    shapely_objects = [path_to_shapely(path) for path in paths_to_draw]
    
    return shapely_objects


def parse_transform(transform):
    """Parse and combine SVG transform string into a single transformation matrix."""
    combined_matrix = np.identity(3)
    for cmd in transform.split(')'):
        if 'matrix' in cmd:
            values = list(map(float, cmd.split('matrix(')[1].split(' ')))
            matrix = np.array([[values[0], values[2], values[4]],
                               [values[1], values[3], values[5]],
                               [0, 0, 1]])
            combined_matrix = matrix @ combined_matrix
        elif 'translate' in cmd:
            values = list(map(float, cmd.split('translate(')[1].split(',')))
            tx, ty = values if len(values) == 2 else (values[0], 0)
            matrix = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]])
            combined_matrix = matrix @ combined_matrix
        elif 'scale' in cmd:
            values = list(map(float, cmd.split('scale(')[1].split(',')))
            sx, sy = values if len(values) == 2 else (values[0], values[0])
            matrix = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
            combined_matrix = matrix @ combined_matrix
        elif 'rotate' in cmd:
            values = list(map(float, cmd.split('rotate(')[1].split(',')))
            angle = np.radians(values[0])
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            if len(values) == 3:
                cx, cy = values[1], values[2]
                matrix = np.array([[cos_a, -sin_a, cx - cx * cos_a + cy * sin_a],
                                   [sin_a, cos_a, cy - cx * sin_a - cy * cos_a],
                                   [0, 0, 1]])
            else:
                matrix = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
            combined_matrix = matrix @ combined_matrix
    return combined_matrix

def collect_transformations(element, namespaces):
    """Recursively collects transformations from an element and its parent nodes."""
    combined_matrix = np.identity(3)
    while element is not None:
        transform_attr = element.attrib.get('transform')
        if transform_attr:
            element_matrix = parse_transform(transform_attr)
            combined_matrix = element_matrix @ combined_matrix
        try:
            element = element.getparent()  # Traverse up to the parent element
        except AttributeError:
            element = None
    return combined_matrix

def transform_arc(arc, matrix):
    """Transforms an Arc segment by adjusting its start/end points, radii, and rotation."""
    # Transform the start and end points
    arc.start = apply_matrix_transform(arc.start, matrix)
    arc.end = apply_matrix_transform(arc.end, matrix)

    # Apply the transformation matrix to the radii (rx, ry) and the rotation angle
    # Convert the rotation to radians for calculation
    rotation_rad = np.radians(arc.rotation)

    # Calculate the new radii by applying the transformation matrix to the ellipse axes
    cos_angle = np.cos(rotation_rad)
    sin_angle = np.sin(rotation_rad)

    # Apply rotation to the x and y axes
    x_axis = np.dot(matrix, np.array([arc.rx * cos_angle, arc.rx * sin_angle, 0]))
    y_axis = np.dot(matrix, np.array([-arc.ry * sin_angle, arc.ry * cos_angle, 0]))

    # The new rx and ry are the magnitudes of the transformed x and y axes
    arc.rx = np.linalg.norm(x_axis[:2])
    arc.ry = np.linalg.norm(y_axis[:2])

    # Update the rotation angle by finding the new angle of the x-axis after transformation
    new_rotation = np.arctan2(x_axis[1], x_axis[0])
    arc.rotation = np.degrees(new_rotation)  # Convert back to degrees

def apply_transform(path, transform):
    path = copy.deepcopy(path)
    """Applies an SVG matrix transformation to each segment's points in the path."""
    if  isinstance(transform, np.ndarray) :
        matrix = transform
        # Apply transformation to each segment in the path
        for segment in path:
            # Apply to start and end points
            segment.start = apply_matrix_transform(segment.start, matrix)
            segment.end = apply_matrix_transform(segment.end, matrix)

            # Transform control points if they exist
            if isinstance(segment, CubicBezier):
                segment.control1 = apply_matrix_transform(segment.control1, matrix)
                segment.control2 = apply_matrix_transform(segment.control2, matrix)
            elif isinstance(segment, QuadraticBezier):
                segment.control = apply_matrix_transform(segment.control, matrix)
            elif isinstance(segment, Arc):
                # Apply transformation to arc radii and rotation
                transform_arc(segment, matrix)
                
    else:
        print('transform is not a matrix')
    return path

def apply_matrix_transform(point, matrix):
    # Apply transformation matrix to a complex point (x, y)
    x, y = point.real, point.imag
    transformed = np.dot(matrix, np.array([x, y, 1]))
    return complex(transformed[0], transformed[1])

    
def interpolate_segment(segment, num_points=20):
    """Generate interpolated points along a segment (Line, Bezier, or Arc)."""
    pass
    return [(segment.point(t).real, segment.point(t).imag) for t in np.linspace(0, 1, num_points)]

def path_to_shapely(path, num_points=20):
    contours = []
    current_contour = []
    
    for segment in path:
        # Start a new contour if needed (e.g., on 'M' or after a closed contour)
        if not current_contour or (current_contour[-1] != (segment.start.real, segment.start.imag)):
            # Complete current contour if it exists
            if current_contour:
                contours.append(current_contour)
            current_contour = [(segment.start.real, segment.start.imag)]
        
        # Interpolate and add points for the current segment
        interpolated_points = interpolate_segment(segment, num_points)
        current_contour.extend(interpolated_points[1:])  # Avoid duplicate start point
    
    # Append the last contour if it's not empty
    if current_contour:
        contours.append(current_contour)

    shapes = []
    for contour in contours:
        p = Polygon(contour)
        hole = False
        for index,shape in enumerate(shapes):
            if shape.contains(p):
                shape = shape.difference(p)
                hole = True
                shapes[index] = shape
                continue
            if p.contains(shape):
                p = p.difference(shape)
                hole = True
                shapes[index] = p
                continue
        if not hole:
            shapes.append(p)
    # Separate outer boundary and holes
    if len(shapes) == 1:
        return Polygon(contours[0])
    else:
        # Sort contours by area to determine the outer boundary and holes
        return shapely.MultiPolygon(shapes)
# Example SVG path with transform

def to_svg(area_list, view_box=None, file_path='test.svg'):
    """Generates an SVG file from a list of Shapely geometries, with customizable view box and output path."""
    # Margin around the bounding box in coordinate units
    margin = 5

    # Determine the bounding box for all geometries in the list
    minx, miny, maxx, maxy = None, None, None, None
    for area in area_list:
        # if not isinstance(area, BaseGeometry):
        #     raise ValueError("All items in area_list must be Shapely geometries.")
        bounds = area.bounds
        minx = min(bounds[0], minx) if minx is not None else bounds[0]
        miny = min(bounds[1], miny) if miny is not None else bounds[1]
        maxx = max(bounds[2], maxx) if maxx is not None else bounds[2]
        maxy = max(bounds[3], maxy) if maxy is not None else bounds[3]

    # Apply margin to the bounding box
    minx -= margin
    miny -= margin
    maxx += margin
    maxy += margin

    # Calculate width and height from the adjusted bounding box
    width = maxx - minx
    height = maxy - miny

    # Define the scale for converting coordinates to pixels
    scale = 1

    # SVG properties
    svg_attributes = {
        'version': '1.1',
        'baseProfile': 'full',
        'width': f'{width * scale:.0f}px',
        'height': f'{height * scale:.0f}px',
        'viewBox': f'{minx:.1f} {miny:.1f} {width:.1f} {height:.1f}',
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:ev': 'http://www.w3.org/2001/xml-events',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink'
    }

    # Generate SVG path data for each geometry in the list
    path_data = "\n".join([area.svg() for area in area_list])

    # Write the SVG file
    with open(file_path, 'w') as f:
        svg_data = textwrap.dedent(f'''
            <?xml version="1.0" encoding="utf-8" ?>
            <svg {' '.join([f'{key:s}="{val:s}"' for key, val in svg_attributes.items()])}>
                {path_data}
            </svg>
        ''')
        f.write(svg_data.strip())
        print(svg_data.strip())

svg_string = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -483 1260 2384" transform="matrix(1 0 0 0 -1 0)">
<defs>
<path id="g72" d="M1151.0,606.0L1151.0,516.0L305.0,516.0Q317.0,326.0 419.5,226.5Q522.0,127.0 705.0,127.0Q811.0,127.0 910.5,153.0Q1010.0,179.0 1108.0,231.0L1108.0,57.0Q1009.0,15.0 905.0,-7.0Q801.0,-29.0 694.0,-29.0Q426.0,-29.0 269.5,127.0Q113.0,283.0 113.0,549.0Q113.0,824.0 261.5,985.5Q410.0,1147.0 662.0,1147.0Q888.0,1147.0 1019.5,1001.5Q1151.0,856.0 1151.0,606.0ZM967.0,660.0Q965.0,811.0 882.5,901.0Q800.0,991.0 664.0,991.0Q510.0,991.0 417.5,904.0Q325.0,817.0 311.0,659.0L967.0,660.0Z"/>
</defs>
<g transform="translate(0,0)">
<use href="#g72"/>
</g>
</svg>'''

from vharfbuzz import Vharfbuzz
vhb = Vharfbuzz('../fonts/vera_sans/Vera.ttf')
buf = vhb.shape('Erik')
# buf = vhb.shape('....')

svg_string = vhb.buf_to_svg(buf)


print(svg_string)

open('test_og.svg', 'w').write(svg_string)
# Convert SVG to Shapely geometry
shapely_objects = parse_svg(svg_string)

class TextToShapely:
    def __init__(self, font='../fonts/vera_sans/Vera.ttf', font_size=100):
        self.vhb = Vharfbuzz(font)

    def __call__(self, text):
        buf = self.vhb.shape(text)
        svg_string = self.vhb.buf_to_svg(buf)
        shapely_objects = parse_svg(svg_string)
        return shapely_objects

text_to_shapely = TextToShapely()

letters = []
for i, a in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    row = i // 5
    col = i % 5
    x = col * 2500
    y = row * 2500

    shapely_objects = text_to_shapely(a)
    letter = shapely.union_all(shapely_objects)
    letter = shapely.affinity.translate(letter, x, y)
    
    letters.append(letter)
    
    print(i, a)
    
# Convert Shapely geometry to SVG

area = shapely.union_all(letters)

areas = [area.buffer(i*50) for i in range(1, 10)]

# to_svg(areas)
to_svg(letters)



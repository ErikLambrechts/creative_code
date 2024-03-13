import argparse
import os
import xml.etree.ElementTree as ET

# Define the layer to color mapping
layer_to_color = {
    'layer1': ('cyan', '#00FFFF'),
    'layer2': ('magenta', '#FF00FF'),
    'layer3': ('yellow', '#FFFF00'),
    'layer4': ('black', '#000000'),
}

# Create the parser and add the file argument
parser = argparse.ArgumentParser(description='Process an SVG file.')
parser.add_argument('file', help='The SVG file to process.')
args = parser.parse_args()

# Check if the file is an SVG file
if not args.file.lower().endswith('.svg'):
    print('The file is not an SVG file.')
    exit(1)

# Parse the SVG file
tree = ET.parse(args.file)
root = tree.getroot()

# Define the SVG namespace
namespaces = {'svg': 'http://www.w3.org/2000/svg'}

svg_dir = os.path.dirname(args.file)
svg_base = os.path.basename(args.file)

# Remove the .svg extension from the base name
svg_name = os.path.splitext(svg_base)[0]

# Create a new directory for the output SVG files
output_dir = os.path.join(svg_dir, f'{svg_name}_output')
os.makedirs(output_dir, exist_ok=True)

# Iterate over all elements in the SVG file
for elem in root.findall('.//*[@id]', namespaces):
    # If the element has an id that is in the layer_to_color dictionary
    if 'id' in elem.attrib and elem.attrib['id'] in layer_to_color:
        # Create a new SVG file with only that element
        new_root = ET.Element('svg', root.attrib)
        new_root.append(elem)
        new_tree = ET.ElementTree(new_root)
        new_tree.getroot().findall('.//*[@id]')[0].attrib['stroke'] = layer_to_color[elem.attrib['id']][1]
        new_tree.write(f'{output_dir}/{layer_to_color[elem.attrib["id"]][0]}.svg')
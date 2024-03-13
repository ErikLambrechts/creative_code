#!/bin/bash

# Check if an argument was provided
if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

# Check if the argument is an SVG file
if [ "${1##*.}" != "svg" ]; then
    echo "The file is not an SVG file"
    exit 1
fi

# Call the Python script with the SVG file as an argument
python3 run.py $1

# Get the directory and base name of the SVG file without the extension
dir=$(dirname $1)
base=$(basename $1 .svg)

# Print the names of all the files in the new output directory
for file in "${dir}/${base}_output"/*; do
    vpype --config vpype.toml read $file gwrite  -p my_own_plotter  "${file%.*}.gcode"
done
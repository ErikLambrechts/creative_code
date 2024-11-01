
import svgutils
import glob

files = glob.glob("output/grid/*.svg")
files = files[:32]

# First list
list1 = [5, 28, 29, 4, 12, 21, 20, 13, 6, 24, 17, 16, 8, 23, 32, 1]
# Second list
list2 = [3, 30, 27, 6, 14, 19, 22, 11, 15, 18, 23, 10, 2, 31, 26, 7]

def reorder_for_booklet(files, list_1, dir_name):
    folder = "output/booklet/" + dir_name 

    rotate = False
    for index, i in enumerate(list_1):
        file_name = f"output/booklet/{dir_name}/{index:02}.svg"
        svg = svgutils.transform.fromfile(files[i-1])
        originalSVG = svgutils.compose.SVG(files[i-1])
        if rotate:
            originalSVG.rotate(180)
            originalSVG.move(svg.height, svg.width)
        figure = svgutils.compose.Figure(svg.height, svg.width, originalSVG)
        figure.save(file_name)

        if index % 4 == 3:
            rotate = not rotate


for list_i, dir_name in [(list1, "front"), (list2, "back")]:
    reorder_for_booklet(files, list_i, dir_name)





    

    
    
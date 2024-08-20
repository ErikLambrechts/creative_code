import vsketch


def walk(i, t):
    global polygons, cameraPos, viewProjectionMatrix, shapes, points
    if i == 0:
        if t < 1:
            enable_progress_bar = False
        polygons = Polygons()
        cameraPos = [camera_distance * math.cos(math.pi * 2 * (camera_angle + t)), camera_height, camera_distance * math.sin(math.pi * 2 * (camera_angle + t))]
        viewProjectionMatrix = setupCamera(cameraPos, cameraLookAt)
        shapes = []
        init_shape()
        bin_shape()
    else:
        if (i % round(1 / split_frequency)) == 0:
            split_shape()

    iterations_t = iterations # math.floor(iterations * t)
    draw_progress_bar(min(i, iterations_t), iterations_t)

    period = math.floor(iterations / layers)

    if i < iterations_t:
        move_shape()
        bin_shape()
        if (i + 1) % period == 0:
            save_shape()
        return True

    if len(shapes) > 0:
        points = shapes.pop()
        # points = shapes.pop(0)
        draw_shape(iterations_t / period - len(shapes))
        return True

    return False

def save_shape(i):
    dpoints = []
    for p in points:
        dpoints.append([p[0], p[1]])
    shapes.append(dpoints)

def draw_progress_bar(i, max):
    if i > 0 and enable_progress_bar:
        i0 = i - 1
        turtle.down()
        x0 = (i0 / max) * 190 - 95
        x1 = (i / max) * 190 - 95
        y = 95
        turtle.jump(x0, y)
        turtle.goto(x1, y)

def get_bin_index(x, y):
    # return 1
    return math.floor(x / bin_size) + math.floor(y / bin_size) * math.ceil(canvas_size / bin_size)

def bin_shape():
    bins = {}

    for id, p in enumerate(points):
        bin_index = get_bin_index(p[0], p[1])
        if bin_index not in bins:
            bins[bin_index] = []
        bins[bin_index].append(id)

def split_shape():
    if len(points) < 2:
        return
    best_pair = 0
    best_distance = math.hypot(points[0][0] - points[1][0], points[0][1] - points[1][1])
    for pair in range(1, len(points)):
        point0 = points[pair]
        point1 = points[(pair + 1) % len(points)]
        distance = math.hypot(point0[0] - point1[0], point0[1] - point1[1])
        if distance > best_distance:
            best_distance = distance
            best_pair = pair

    new_points = [
        list(points[0])
    ]
    for pair in range(len(points)):
        point0 = points[pair]
        point1 = points[(pair + 1) % len(points)]
        if pair == best_pair:
            x = (point0[0] + point1[0]) / 2
            y = (point0[1] + point1[1]) / 2
            new_point = [x, y]
            new_points.append(new_point)
        if pair < len(points) - 1:
            new_points.append(point1)
            


class DifferentialGrowth(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        amera_angle = vsketch.Param(0.14, min_value=0, max_value=1, step=0.01)
        camera_height = vsketch.Param(150, min_value=0, max_value=500, step=50)
        camera_distance = 400
        exaggeration = vsketch.Param(1, min_value=0, max_value=5, step=0.1)

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    DifferentialGrowth.display()

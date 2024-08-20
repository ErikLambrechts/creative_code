import vsketch


class CirclePacking1(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)
    hide_radius = vsketch.Param(5, min_value=0, max_value=20, step=1)
    max_radius = vsketch.Param(10, min_value=0.01, max_value=20, step=0.01)
    min_radius = vsketch.Param(0.3, min_value=0.01, max_value=2, step=0.01)
    shape = vsketch.Param(1, min_value=0, max_value=1, step=1)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        canvas_size = 95
        radius_decr = .99
        max_tries = 5000

        radius = self.max_radius

        circles = []
        import random

        circles = []

        def add_circle(r):
            coord_found = False
            tries = 0

            while not coord_found and tries < max_tries:
                tries += 1

                x = random.random() * (canvas_size - r) * 2 - canvas_size + r
                y = random.random() * (canvas_size - r) * 2 - canvas_size + r
                possible = True
                for i in range(len(circles)):
                    dx = circles[i][0] - x
                    dy = circles[i][1] - y
                    dr = circles[i][2] + r

                    if dx * dx + dy * dy < dr * dr or (self.shape and x * x + y * y > (canvas_size - r) * (canvas_size - r)):
                        possible = False
                        break
                if possible and (not self.shape or x * x + y * y < (canvas_size - r) * (canvas_size - r)):
                    coord_found = True
                    if r <= self.hide_radius:
                        vsk.circle(x, y , r, mode="radius")
                    circles.append([x, y, r])
                    return True
            return False
                # implement your sketch here
                # vsk.circle(0, 0, self.radius, mode="radius")

        while radius >= self.min_radius:
            print(radius)   
            if (not add_circle( radius)) :
                radius *= radius_decr
        
        print(circles)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CirclePacking1.display()

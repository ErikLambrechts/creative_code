import random
import vsketch


class Bubbles(vsketch.SketchClass):

    def add_circle(self, x, y, r):
        for c in self.circles:
            x0, y0, r0 = c
            d = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
            if d < r0 + 0.1:
                return
            r_max = max(d-r0, r)
        self.circles.append([x, y, r_max])

    def random_circle(self):
        r = random.random() * self.max_circle_size.value
        if r < 0.3:
            r = 0.5
        trace = 1

        x = random.random() * 2 * (self.width.value - r) - self.width.value + r
        y = random.random() * 2 * (self.height.value - r) - self.height.value + r
        return x, y, r

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        max_circle_size = vsketch.Param(20, 5, 80, 1)
        height = vsketch.Param(90, 10, 100, 1)
        width = vsketch.Param(45, 10, 100, 1)
        depth = vsketch.Param(10, 1, 10, 0.5)

        self.circles = []

        for _ in range(1000):
            x, y, r = self.random_circle()
            self.add_circle(x, y, r)

        for c in self.circles:
            x,y,r = c
            vsk.circle(x,y,r, mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    Bubbles.display()

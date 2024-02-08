import numpy as np
import vsketch


class MixingCurlNoiseFields(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def fbm(self, x, y, z, octaves, frequency, amplitude):
        value = 0
        for i in range(octaves):
            value += noise.snoise3(x * frequency, y * frequency, z * frequency) * amplitude
            frequency *= 2
            amplitude *= 0.5
        return value
    
    def field(self,x,y):
        n = self.fieldFrequency / self.frequency
        return self.fmb(x*n-100, y*n) < 0 


    def curlNoise(self, x, y, turtle_field, radius):
        eps = 0.01
        x += 100 if turtle_field == 1 else 500

        dx = (self.fbm(x, y + eps) - self.fbm(x, y - eps)) / (2 * eps)
        dy = (self.fbm(x + eps, y) - self.fbm(x - eps, y)) / (2 * eps)

        l = np.hypot(dx, dy) / radius * .99
        return [dx / l, -dy / l]


    def walk(self, i, turtle, maxPathLength, grid, maxTries, fieldFrequency, frequency, field):
        p = turtle.pos()

        curl = self.curlNoise(p[0], p[1])
        dest = [p[0] + curl[0], p[1] + curl[1]]

        if (turtle.traveled < maxPathLength and
            abs(dest[0]) < 110 and abs(dest[1]) < 110 and
            grid.insert(dest)):

            turtle.goto(dest)
            turtle.traveled += np.hypot(curl[0], curl[1])
        else:
            turtle.traveled = 0
            r, i = None, 0
            while not grid.insert(r) and i < maxTries:
                r = [np.random.random() * 200 - 100, np.random.random() * 200 - 100]
                i += 1
            if i >= maxTries:
                return False
            turtle.jump(r)
            n = fieldFrequency / frequency
            turtle.field = field(r[0], r[1])
        return True

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        seed = vsketch.Param(78, min_value=1, max_value=100, step=1)
        radius = vsketch.Param(1.8, min_value=0.1, max_value=5, step=0.01)
        maxPathLength = vsketch.Param(50, min_value=1, max_value=100, step=0.1)
        frequency = vsketch.Param(0.3, min_value=0.1, max_value=10, step=0.01)
        fieldFrequency = vsketch.Param(5, min_value=0.1, max_value=10, step=0.01)

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MixingCurlNoiseFields.display()

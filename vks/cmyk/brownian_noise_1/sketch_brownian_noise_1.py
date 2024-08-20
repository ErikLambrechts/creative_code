import math
import scipy.interpolate as spi
import vsketch
import numpy as np

import pymc as pm


class BrownianNoise1Sketch(vsketch.SketchClass):
    # Sketch parameters:
    radius = vsketch.Param(2.0)
    scale = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        N = 10000
        def samples(N):
            def density(x, y):
                return (np.exp(-(x ** 2 + y ** 2) / 4) - np.exp(-(x ** 2 + y ** 2) / 16))**3

            scale = self.scale
            # Define the proposal distribution
            def proposal(x, y):
                return [x + scale * np.random.normal(), y +  scale *np.random.normal()]
            # Initialize the MCMC sampler
            x, y = 0., 1.
            samples = [(x, y)]

            # Number of iterations

            for _ in range(N):
                x_proposed, y_proposed = proposal(x, y)
                prob_accept = min(1, density(x_proposed, y_proposed) / density(x, y))
                
                if np.random.rand() < prob_accept:
                    x, y = x_proposed, y_proposed
                
                samples.append((x, y))

            # Convert the samples to a NumPy array
            samples = np.array(samples)
            return samples

        for stroke, offset in [
            [1, [0, 1]],
            [2, [math.sqrt(3)/2, -0.5]],
            [3, [-math.sqrt(3)/2, -0.5]],
        ]:
            samples_ = (samples(N)*1.5 + np.array(offset)*2) *0.8
            x = samples_[:, 0]
            y = samples_[:, 1]

            t = range(len(x))
            t_fine = np.arange(0, len(x), 0.1)
            fsmooth_x = spi.InterpolatedUnivariateSpline(t, x,k=2)
            fsmooth_y = spi.InterpolatedUnivariateSpline(t, y,k=2)
            x = fsmooth_x(t_fine)
            y = fsmooth_y(t_fine)
            vsk.stroke(stroke)
            # for i in range(0, N-1, 3):
            for i in range(0, N-1):
                vsk.line(x[i], y[i], x[i+1], y[i+1])

            # vsk.stroke(2)
            # for i in range(1, N-1, 3):
            #     vsk.line(x[i], y[i], x[i+1], y[i+1])

            # vsk.stroke(3)
            # for i in range(2, N-1, 3):
            #     vsk.line(x[i], y[i], x[i+1], y[i+1])


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    BrownianNoise1Sketch.display()

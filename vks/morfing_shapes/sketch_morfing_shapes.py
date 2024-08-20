import numpy as np
import vsketch
import opensimplex

import numpy as np

import matplotlib.pyplot as plt

from matplotlib.collections import PatchCollection

from scipy.stats import qmc


from scipy.spatial import Voronoi, voronoi_plot_2d




class MorfingShapesSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("1cm")

        radius = 0.01

        rng = np.random.default_rng()
        engine = qmc.PoissonDisk(d=2, radius=radius, seed=rng)

        sample = engine.random(21) * 20
        print(sample)



        vor = Voronoi(sample)
        
        for point in sample:
            vsk.circle(point[0], point[1], 0.1, mode="radius")

        # for point in vor.vertices:
        #     vsk.stroke(1)
        #     vsk.circle(point[0], point[1], 0.15, mode="radius")

        for region in vor.regions:
            if not -1 in region and region:
                # print(region)
                polygon = np.array([vor.vertices[i] for i in region])
                # print(polygon.T)
                vsk.polygon(*(polygon.T))


        # x = np.arange(0, 10, 0.1)
        
        # for t in np.arange(0, 10, 0.1):

        #     y =[ t+ opensimplex.noise4(_x, t, 0,0) for _x in x]

        #     vsk.polygon(x,y)


        vsk.scale("1cm")

        vsk.vpype("crop 0 0 10cm 10cm ")
        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MorfingShapesSketch.display()

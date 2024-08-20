import random
import numpy as np
import shapely
import vsketch
import noise

class FlowFieldsSketch(vsketch.SketchClass):
    # Sketch parameters:
    dt = vsketch.Param(0.5)
    dikte = vsketch.Param(0.5)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")


        # Generate simplex noise
        scale = .10  # scale of the noise
        octaves = 3  # number of noise octaves, higher values give more detail
        persistence = 0.9  # persistence of the noise, higher values give smoother noise
        lacunarity = 2.0  # lacunarity of the noise, higher values give more gaps in the noise

        dx = random.randint(0, 100) * 1
        dy = random.randint(0, 100) * 1

        dt = self.dt


        def worm(curve):
            length = 0
            for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
                length += ((x1-x0)**2 + (y1-y0)**2)**0.5

            spline = shapely.LineString(curve)

            offset_r = spline.parallel_offset(self.dikte, 'right')
            offset_l = spline.parallel_offset(self.dikte, 'left' )


            length_sements = np.arange(0, offset_r.length, 0.6)
            # points_r = [[offset_r.interpolate(t) for t in np.arange(start, end, 0.001)] for start, end in zip(length_sements, length_sements[1:])]
            # points_l = [[offset_l.interpolate(t) for t in np.arange(start, end, 0.001)] for start, end in zip(length_sements, length_sements[1:])]

            # points = [[spline.interpolate(t) for t in np.arange(start, end, 0.001)] for start, end in zip(length_sements, length_sements[1:])]
            
            vsk.stroke(3)
                
            # for p in points:
            #     p = shapely.LineString(p)
            #     p_r = p.parallel_offset(self.dikte, 'right')
            #     p_l = p.parallel_offset(self.dikte, 'left')
            #     segment = shapely.Polygon(list(p_r.coords) + p_l.coords[::-1])
            #     segment = segment.simplify(tolerance=0.01)
            #     vsk.polygon(segment.exterior.coords)


            points = [spline.interpolate(t) for t in np.arange(0, length, 0.6)]

            line = shapely.LineString(points)
            offset_r = line.parallel_offset(self.dikte, 'right', join_style='mitre', mitre_limit=10.0)
            offset_l = line.parallel_offset(self.dikte, 'left', join_style='mitre', mitre_limit=10.0)


            vsk.stroke(2)
            # vsk.polygon(line.coords)
            # vsk.polygon(offset_r.coords)
            # vsk.polygon(offset_l.coords)
            vsk.stroke(4)
            for line in zip(offset_r.coords, offset_r.coords[1:], offset_l.coords[1:], offset_l.coords):
            # for l in zip(offset_r, offset_r[1:]):
                r0, r1, l1, l0 = line

                vsk.stroke(3)
                # vsk.line(*r0, *l0)
                vsk.stroke(3)

                d = 0.1

                r = shapely.LineString([r0, r1])
                dr = d - (r.length + 0.6)/4
                dr = (-r.length + 0.6)/2
                # r0 = r.interpolate((r.length -0.6)/2)
                # r1 = r.interpolate((r.length + 0.6)/2)

                l = shapely.LineString([l0, l1])
                dl = d - (l.length + 0.6)/4
                dl = (l.length + 0.6)/2
                # l0 = l.interpolate((l.length -0.6)/2)
                # l1 = l.interpolate((l.length + 0.6)/2)
                # l0 = l.interpolate(dl)
                # l1 = l.interpolate(l.length - dl)

                d = 0.2
                s = shapely.Polygon([r0, r1, l1, l0])
                # print([r0, r1.coords, l1.coords, l0.coords])
                # s = s.buffer(-d).buffer(d)

                # print(*r0, *l0)
                # vsk.fill(6)
                vsk.polygon(s.exterior.coords)
                vsk.stroke(4)
                # vsk.polygon(line)

                # use shapely to offset the line segements in segment_bases






        for l in range(1):
            vsk.stroke(l+1)

            layer = l /100


            for _x in range(0, 1):
                for _y in range(0, 1):
                    x = _x 
                    y = _y 
                    curve = [(x,y)]
                    for _ in range(0, 100):
                        value0 = dt * noise.snoise3(x * scale+ dx, y * scale+ dy, 2*layer + 0, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                        value1 = dt * noise.snoise3(x * scale+ dx, y * scale+ dy, 2*layer + 1, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                        # do something with the noise value here, for example draw a point
                        vsk.line(x, y, x + value0, y + value1)
                        x += value0
                        y += value1
                        curve.append((x,y))
                    x = _x
                    y = _y
                    curve.reverse()
                    for _ in range(0, 100):
                        value0 = dt * noise.snoise3(x * scale+ dx, y * scale+ dy, 2*layer + 0, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                        value1 = dt * noise.snoise3(x * scale+ dx, y * scale+ dy, 2*layer + 1, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
                        # do something with the noise value here, for example draw a point
                        vsk.line(x, y, x - value0, y - value1)
                        x -= value0
                        y -= value1
                        curve.append((x,y))

                    worm(curve)
        vsk.vpype("occult -i")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("occult linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FlowFieldsSketch.display()
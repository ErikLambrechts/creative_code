import math
import random
from scipy.linalg import svd
from numpy.linalg import inv
import numpy as np
import vsketch
from shapely import geometry
import shapely
from skimage import transform


class TriangularGrid:
    def __init__(self, n):
        self.n = n
        self.plane_offset = (3*n - 2)//2

        self.init_grid()
        self.masks = [
            # 4,
        ]
        self.active_mask = None


    def make_mask(self, offset, symmetric=True):
        mask = np.zeros([self.n,self.n,self.n], dtype=bool)
        for i in range(self.n): 
            for j in range(self.n):
                for k in range(self.n):
                    if (i+j+k - self.plane_offset)== offset:
                        mask[i,j,k] = True
                    if symmetric and (i+j+k - self.plane_offset)== -offset:
                        mask[i,j,k] = True
        return mask

    def init_grid(self, max_size=None, max_size_min=None):
        self.grid = np.ones([self.n,self.n,self.n], dtype=bool)
        if max_size is None:
            max_size = self.n * 3
        if max_size_min is None:
            max_size_min = -max_size
        for i in range(self.n): 
            for j in range(self.n):
                for k in range(self.n):
                    if (i+j+k) == self.plane_offset:
                        self.grid[i,j,k] = False
                    if (i+j+k - self.plane_offset) < max_size_min or (i+j+k - self.plane_offset) > max_size:
                        self.grid[i,j,k] = False
                
    
    def nr_valid_option(self):
        return (self.grid & self.active_mask).sum()

    def get_valid_cell_by_index(self,cell_index):
        for i in range(self.n):
            for j in range(self.n):
                for k in range(self.n):
                    if self.grid[i,j,k] and self.active_mask[i,j,k]:
                        if cell_index == 0:
                            return [i,j,k]
                        cell_index -= 1
    
    def update_grid_with_tri(self, tri):
        i,j,k = tri

        diff = i+j+k-self.plane_offset

        for i_ in range(min(i, i - diff), max(i, i - diff) + 1):
            for j_ in range(min(j, j - diff), max(j, j - diff) + 1):

                def _set_grid_invalid(offset):
                    k_ = self.plane_offset - i_ - j_  
                    if diff < 0:
                        k_ -= offset
                    else:
                        k_ += offset

                    if k_ >= min(k, k - diff) and k_ <=  max(k, k - diff):
                        if i_ < 0 or j_ < 0 or k_ < 0 or i_ >= self.n or j_ >= self.n or k_ >= self.n: 
                            return

                        if diff > 0:
                            self.grid[i_:,j_:,k_:] = False
                            self.grid[:i_,:j_,:k_] = False
                        else:
                            self.grid[:i_+1,:j_+1,:k_+1] = False
                            self.grid[i_+1:,j_+1:,k_+1:] = False

                _set_grid_invalid(1)
                _set_grid_invalid(2)

    def finished(self):
        return self.grid.sum() == 0

    def update_mask(self):
        if self.active_mask is None or self.active_mask.sum() == 0:

            self.active_mask = np.ones([self.n,self.n,self.n], dtype=bool)

            if self.masks:
                offsets = self.masks.pop(0)

                if isinstance(offsets, int):
                    offsets = [offsets]
            
                for offset in offsets:
                    self.active_mask &= self.make_mask(offset)
            
        self.active_mask &= self.grid

        if self.active_mask.sum() == 0:
            self.update_mask()

    def sample(self):
        self.triangles = []

        while not self.finished():

            self.update_mask()

            tri = self.get_random_tri()
            self.triangles.append(tri)
            
            self.update_grid_with_tri(tri)
    def sample_aligned(self):
        self.triangles = []
        self.plane_offset = 0

        n = 8
        tri_remaining = [
            [n,0,0],
            [0,n,0],
            [0,0,n],
            [-n,0,0],
            [0,-n,0],
            [0,0,-n],
        ] 

        max_offset = 2
        while tri_remaining:
            tri = tri_remaining.pop(0)

            offset = tri[0]+tri[1]+tri[2]
            if abs(offset) <= 2**3 and (random.random() > 0.7 or  abs(tri[0]+tri[1]+tri[2]) <= 1):
                self.triangles.append(tri)
            
            else:

                tri_remaining.append([tri[0]-offset//2,tri[1],tri[2]])
                tri_remaining.append([tri[0],tri[1]-offset//2,tri[2]])
                tri_remaining.append([tri[0],tri[1],tri[2]-offset//2])
                tri_remaining.append([tri[0]-offset//2,tri[1]-offset//2,tri[2]-offset//2])

    
    def get_random_tri(self):
        m = self.nr_valid_option()
        cell_index= np.random.randint(0,m)
        tri = self.get_valid_cell_by_index(cell_index)
        return tri

def estimate_transform(src, dst):
    # Pad the data with ones, so that our transformation can do translations too
    src = np.array([[p[0], p[1], 1] for p in src])
    dst = np.array([[p[0], p[1], 1] for p in dst])

    T = np.dot(inv(src), dst)

    return T[:,:2]

def apply_transform(T, src):
    src = np.array([[p[0], p[1], 1] for p in src])
    return np.dot(src, T)

class MoreMultiScaleTruchetTiles(vsketch.SketchClass):
    grid_size = vsketch.Param(1.0, min_value=0.1, max_value=5, step=.1) 
    offset_size = vsketch.Param(.1, min_value=0.01, max_value=1, step=.01) 
    bevel_size = vsketch.Param(.1, min_value=0.01, max_value=1, step=.01) 
    max_triangle_size = vsketch.Param(10, min_value=1, max_value=10, step=1) 
    multiplier = vsketch.Param(1, min_value=1, max_value=4, step=1) 
    debug = vsketch.Param(True) 

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        grid = TriangularGrid(10)
        grid.init_grid(max_size=self.max_triangle_size)



        # grid.sample()
        grid.sample_aligned()

        
        def draw_debug(p0, p1, p2, diff):

            triangle = geometry.Polygon([p0, p1, p2])
            vsk.geometry(triangle)
            # for a,b in [[p0,p1],[p1,p2],[p2,p0]]:
            #     # skuw the triangle to make it equilateral
            #     vsk.line(a[0], a[1], b[0], b[1])    


        def draw_offset(p0, p1, p2, diff, offset_value=-0.3, bevel=0.3):
            tri = geometry.Polygon([p0, p1, p2])
            offset = shapely.offset_curve(tri, offset_value-bevel, join_style='round')
            offset = geometry.Polygon(offset)
            offset = shapely.offset_curve(offset, bevel, join_style='round')
            vsk.geometry(offset)

        waves_cashed = {}
        def draw_waves(p0, p1, p2, diff):

            diff = abs(diff)

            def base_points(diff):
                return [ (np.cos(i*np.pi*2/3), np.sin(i*np.pi*2/3)) for i in range(3)]

            def base_wave(diff):
                points = base_points(diff)

                triangle = geometry.Polygon(
                    points
                )

                length_side = np.linalg.norm(np.array(points[0])-np.array(points[1]))

                data = []

                radia = [ (0.5 + i) / (self.multiplier  * 2  * diff)for i in range(abs(diff * 2 * self.multiplier) )]
                radia = [ i for i in radia if i <= 0.79]
                radia = [ alpha * length_side  for alpha in radia]
                for i in radia:
                    circle = geometry.Point(points[0]).buffer(i)
                    arc = shapely.intersection(circle.exterior, triangle)
                    data.append(arc)


                radius = np.max(radia)
                other = triangle.difference(geometry.Point(points[0]).buffer(radius))
                radia = [ (0.5 + i) / (self.multiplier  * 2  * abs(diff))for i in range(abs(diff * 2 * self.multiplier) )]
                radia = radia[:len(radia)//2+1]
                radia = [ alpha * length_side  for alpha in radia]

                for p in points[1:]:
                    for i in radia:
                        circle = geometry.Point(p).buffer(i)
                        arc = shapely.intersection(circle.exterior, other)
                        data.append(arc)
                    radia.pop(-1)

                return data

            if diff not in waves_cashed.keys():
                waves_cashed[diff] = (base_points(diff), base_wave(diff))

            base_points_diff, base_wave_diff =  waves_cashed[diff] 

            points = [p0, p1, p2]
            points.sort(key=lambda x: random.random())

            tform = estimate_transform(np.array(base_points_diff), np.array(points))

            for arc in base_wave_diff:
                arc = apply_transform(tform, arc.coords)

                vsk.geometry(shapely.LineString(arc))

        for tri in grid.triangles:
            i,j,k = tri
            diff = i+j+k-grid.plane_offset
            def transform(i,j,k):
                return np.array([(i-j)*np.sqrt(3)/2,  (i+j)/2 - k])*self.grid_size
            p0 = transform(i,j,k-diff)
            p1 = transform(i,j-diff,k)
            p2 = transform(i-diff,j,k)

            if self.debug:
                draw_debug(p0, p1, p2, diff)
            # draw_offset(p0, p1, p2, diff, -self.offset_size, self.bevel_size)
            draw_waves(p0, p1, p2, diff)


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MoreMultiScaleTruchetTiles.display()
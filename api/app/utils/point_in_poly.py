import numpy as np
from shapely.geometry import Point, Polygon

def point_in_poly(pt, ply):
    # print(ply)
    ply = np.asarray(ply)
    ply = ply.flatten()
    ply = np.reshape(ply, (4, 2))
    # print(ply.tolist())
    point = Point(pt)
    poly = Polygon(ply)
    return poly.contains(point)
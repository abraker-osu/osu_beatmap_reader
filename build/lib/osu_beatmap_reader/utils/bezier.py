import numpy as np

from .misc import bernstein


class Bezier():
    APPROX_LEVEL = 4

    def __init__(self, curve_points, length_bound):
        # estimate the length of the curve
        diffs = np.subtract(curve_points[1:], curve_points[:-1])
        approx_length = np.sum(np.sqrt(np.einsum('...i,...i', diffs, diffs)))

        # subdivide the curve
        subdivisions = int(min(approx_length, length_bound) / Bezier.APPROX_LEVEL) + 2
        self.curve_points = Bezier.point_at(curve_points, np.linspace(0, 1, subdivisions))


    @staticmethod
    def point_at(curve_points, t):
        n = len(curve_points) - 1
        return sum(
            np.expand_dims(bernstein(i, n, t), -1) * p
            for i, p in enumerate(curve_points)
        )

import math
import numpy as np

from ...utils.bezier import Bezier
from ...utils.misc import triangle, lerp, value_to_percent

from ..hitobject import Hitobject



class StdHoldNoteHitobjectBase(Hitobject):

    LINEAR1       = 'L'
    LINEAR2       = 'C'
    BEZIER        = 'B'
    CIRCUMSCRIBED = 'P'

    def __init__(self):
        self.end_time     = None    # Initialized by beatmapIO.__process_slider_timings after timing data is read
        self.pixel_length = None
        self.repeat       = None
        self.curve_type   = None

        self.to_repeat_time   = None

        self.curve_points = []  # Points that define slider in editor
        self.gen_points   = []  # The rough generated slider curve
        self.tick_times   = []  # Slider ticks/score points/aimpoints

        Hitobject.__init__(self)
        

    def time_to_percent(self, time):
        return value_to_percent(self.time, self.end_time, time)


    def time_to_pos(self, time):
        return self.percent_to_pos(self.time_to_percent(time))


    def percent_to_idx(self, percent):
        if percent < 0.0: return 0
        if percent > 1.0: return -1 if self.repeat == 0 else 0

        idx = percent*len(self.gen_points)
        idx_pos = triangle(idx*self.repeat, (2 * len(self.gen_points)) - 1)
        
        return int(idx_pos)


    def idx_to_pos(self, idx):
        if idx > len(self.gen_points) - 2:
            return self.gen_points[-1]

        percent_point = float(int(idx)) - idx
        x_pos = lerp(self.gen_points[idx][0], self.gen_points[idx + 1][0], percent_point)
        y_pos = lerp(self.gen_points[idx][1], self.gen_points[idx + 1][1], percent_point)

        return np.asarray([ x_pos, y_pos ])


    def percent_to_pos(self, percent):
        return self.idx_to_pos(self.percent_to_idx(percent))


    def get_end_time(self):
        return self.end_time


    def get_generated_curve_points(self):
        return self.gen_points


    def get_last_tick_time(self):
        return self.tick_times[-1]


    def get_aimpoint_times(self):
        return self.tick_times


    # TODO: make sure this is correct
    # TODO: test a slider 200px across with various repeat times and tick spacings
    def get_velocity(self):
        return self.pixel_length / (self.end_time - self.time)


    def time_changed(self, time):
        self.slider_point_pos = self.time_to_pos(time)
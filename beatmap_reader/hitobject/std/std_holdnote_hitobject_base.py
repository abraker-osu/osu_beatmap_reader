import math
import numpy as np

from ...utils.bezier import Bezier
from ...utils.misc import triangle, intersect, lerp, dist, value_to_percent

from ..hitobject import Hitobject



class StdHoldNoteHitobjectBase(Hitobject):

    LINEAR1       = 'L'
    LINEAR2       = 'C'
    BEZIER        = 'B'
    CIRCUMSCRIBED = 'P'

    def __init__(self, **kargs):
        Hitobject.__init__(self, **kargs)

        curve_type, curve_points = self.__process_slider_data(kargs['sdata'])

        # The rough generated slider curve
        self.gen_points = self.__process_curve_points(curve_type, curve_points, kargs['px_len'])
        
        self.px_len       = kargs['px_len']
        self.repeats      = kargs['repeats']
        self.curve_type   = curve_type
        self.curve_points = curve_points  # Points that define slider in editor
        

    def generate_tick_data(self, **kargs):
        self.hdata[Hitobject.HDATA_TEND] = kargs['end_time']
        ms_per_beat = (100.0 * kargs['sm'])/(self.get_velocity() * kargs['st'])

        for beat_time in np.arange(self.start_time(), self.end_time(), ms_per_beat):
            x_pos, y_pos = self.time_to_pos(beat_time)
            self.tdata.append([ x_pos, y_pos, beat_time ])

        if self.tdata[-1][Hitobject.TDATA_T] != self.end_time():
            x_pos, y_pos = self.time_to_pos(self.end_time())
            self.tdata.append([ x_pos, y_pos, self.end_time() ])


    def time_to_pos(self, time):
        return self.__idx_to_pos(self.__percent_to_idx(value_to_percent(self.start_time(), self.end_time(), time)))


    # TODO: make sure this is correct
    # TODO: test a slider 200px across with various repeat times and tick spacings
    def get_velocity(self):
        return self.px_len / (self.end_time() - self.start_time())


    def __idx_to_pos(self, idx):
        if idx > len(self.gen_points) - 2:
            return self.gen_points[-1]

        percent_point = float(int(idx)) - idx
        x_pos = lerp(self.gen_points[idx][0], self.gen_points[idx + 1][0], percent_point)
        y_pos = lerp(self.gen_points[idx][1], self.gen_points[idx + 1][1], percent_point)

        return x_pos, y_pos


    def __percent_to_idx(self, percent):
        if percent < 0.0: return 0
        if percent > 1.0: return -1 if self.repeats == 0 else 0

        idx = percent*len(self.gen_points)
        idx_pos = triangle(idx*self.repeats, (2 * len(self.gen_points)) - 1)
        
        return int(idx_pos)


    def __process_slider_data(self, sdata):
        slider_data = sdata.split('|')
        curve_type = slider_data[0].strip()

        # The first actual point is the slider's starting position, followed by all other read points
        curve_points = [ [ self.pos_x(), self.pos_y() ] ]

        for curve_data in slider_data[1:]:
            curve_data = curve_data.split(':')
            curve_points.append([ int(curve_data[0]), int(curve_data[1]) ])

        return curve_type, curve_points

    
    def __process_curve_points(self, curve_type, curve_points, px_len):
        gen_points  = []
        
        if curve_type == StdHoldNoteHitobjectBase.BEZIER:
            return self.__make_bezier(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.CIRCUMSCRIBED:
            if len(curve_points) == 3:
                gen_points = self.__make_circumscribed(curve_points, px_len)
                if len(gen_points) == 0:
                    return self.__make_bezier(curve_points)
            
            return self.__make_bezier(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.LINEAR1:
            return self.__make_linear(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.LINEAR2:
            return self.__make_linear(curve_points)


    def __make_linear(self, curve_points):
        gen_points = []

        # Lines: generate a new curve for each sequential pair
        # ab  bc  cd  de  ef  fg
        for i in range(len(curve_points) - 1):
            bezier = Bezier([ curve_points[i], curve_points[i + 1] ])
            gen_points.append(bezier.curve_points)

        return gen_points


    def __make_bezier(self, curve_points):
        gen_points = []

        # Beziers: splits points into different Beziers if has the same points (red points)
        # a b c - c d - d e f g
        point_section = []

        for i in range(len(curve_points)):
            point_section.append(curve_points[i])

            not_end_of_list = (i < len(curve_points) - 1)
            segment_bezier  = (curve_points[i] == curve_points[i + 1]) if not_end_of_list else True

            # If we reached a red point or the end of the point list, then segment the bezier
            if segment_bezier:
                gen_points += Bezier(point_section).curve_points
                point_section = []

        return gen_points


    def __make_circumscribed(self, curve_points, px_len):
        gen_points = []

        # construct the three points
        start = np.asarray(curve_points[0])
        mid   = np.asarray(curve_points[1])
        end   = np.asarray(curve_points[2])

        # find the circle center
        mida = (start + mid)/2   # midpoint
        midb = (end + mid)/2     # midpoint
        nora = np.asarray([ start[1] - mid[1], mid[0] - start[0] ])   # This is turning it into (-y, x)
        norb = np.asarray([ end[1]   - mid[1], mid[0] - end[0] ])
        
        circle_center = intersect(mida, nora, midb, norb)
        if type(circle_center) == type(None):
            return gen_points

        start_angle_point = start - circle_center
        mid_angle_point   = mid - circle_center
        end_angle_point   = end - circle_center

        start_angle = math.atan2(start_angle_point[1], start_angle_point[0])  # It's math.atan2(y, x)
        mid_angle   = math.atan2(mid_angle_point[1], mid_angle_point[0])
        end_angle   = math.atan2(end_angle_point[1], end_angle_point[0])

        if not start_angle < mid_angle < end_angle:
            if abs(start_angle + 2*math.pi - end_angle) < 2*math.pi and (start_angle + 2*math.pi < mid_angle < end_angle):
                start_angle += 2*math.pi
            elif abs(start_angle - (end_angle + 2*math.pi)) < 2*math.pi and (start_angle < mid_angle < end_angle + 2*math.pi):
                end_angle += 2*math.pi
            elif abs(start_angle - 2*math.pi - end_angle) < 2*math.pi and (start_angle - 2*math.pi < mid_angle < end_angle):
                start_angle -= 2*math.pi
            elif abs(start_angle - (end_angle - 2*math.pi)) < 2*math.pi and (start_angle < mid_angle < end_angle - 2*math.pi):
                end_angle -= 2*math.pi   
            else:
                print('Cannot find angles between mid_angle')
                return gen_points

        # find an angle with an arc length of pixelLength along this circle
        radius = dist(start_angle_point, [ 0, 0 ])
        arc_angle = px_len / radius                                                                  # len = theta * r / theta = len / r
        end_angle = start_angle + arc_angle if end_angle > start_angle else start_angle - arc_angle  # now use it for our new end angle

        # Calculate points
        step = px_len / 5  # 5 = CURVE_POINTS_SEPERATION
        len = int(step) + 1

        for i in range(len):
            ang = lerp(start_angle, end_angle, i/step)
            xy  = [ math.cos(ang)*radius + circle_center[0], math.sin(ang)*radius + circle_center[1] ]
            gen_points.append(xy)
        
        return gen_points
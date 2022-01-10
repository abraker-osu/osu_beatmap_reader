import math
import numpy as np

from ...utils.bezier import Bezier
from ...utils.misc import triangle, intersect, lerp, dist, value_to_percent, binary_search, frange

from ..hitobject import Hitobject



class StdHoldNoteHitobjectBase(Hitobject):

    PRECISION_THRESHOLD_PX = 0.01

    ARC_PARALLEL_THRESHOLD = 0.00001

    CURVE_POINTS_SEPARATION = 5

    TICK_CUTOFF_MS = 10
    """
    Ticks closer to the end time of the slider than this are not generated.

    Value: https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderEventGenerator.cs#L24
    """

    END_TICK_OFFSET_MS = 36
    """
    The tick for sliderend judgement is offset backwards in time by this amount
    unless the slider is particularly short.

    Value: https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/Legacy/ConvertSlider.cs#L52
    Usage: https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderEventGenerator.cs#L79
    """

    LINEAR1       = 'L'
    LINEAR2       = 'C'
    BEZIER        = 'B'
    CIRCUMSCRIBED = 'P'

    def __init__(self, **kargs):
        Hitobject.__init__(self, **kargs)

        curve_type, curve_points = self.__process_slider_data(kargs['sdata'])

        # The rough generated slider curve
        gen_points = StdHoldNoteHitobjectBase.__process_curve_points(curve_type, curve_points, kargs['px_len'])
        length_sums = StdHoldNoteHitobjectBase.__calculate_length_sums(gen_points)

        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderPath.cs#L284
        extend = len(curve_points) >= 2 and curve_points[-1] != curve_points[-2]
        StdHoldNoteHitobjectBase.__snap_path_length(gen_points, length_sums, kargs['px_len'], extend)
        
        self.gen_points = gen_points
        self.length_sums = length_sums
        self.px_len       = kargs['px_len']
        self.repeats      = kargs['repeats']
        self.curve_type   = curve_type
        self.curve_points = curve_points  # Points that define slider in editor
        

    def generate_tick_data(self, **kargs):
        self.hdata[Hitobject.HDATA_TEND] = kargs['end_time']
        if self.end_time() == self.start_time():
            pos = self.hdata[Hitobject.HDATA_POSX], self.hdata[Hitobject.HDATA_POSY]
            self.tdata.append([ *pos, self.start_time() ])
            return

        velocity = kargs['velocity']
        ms_per_beat = kargs['beat_length'] / kargs['tick_rate']
        ms_per_repeat = self.px_len / velocity

        tick_times = list(frange(self.start_time() + ms_per_beat, self.start_time() + ms_per_repeat, ms_per_beat))
        cutoff_dist = self.px_len - StdHoldNoteHitobjectBase.TICK_CUTOFF_MS * velocity
        while len(tick_times) > 0 and self.__time_to_dist(tick_times[-1]) > cutoff_dist:
            tick_times.pop()
        ticks = [ (self.time_to_pos(tick_time), tick_time - self.start_time()) for tick_time in tick_times ]

        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderEventGenerator.cs#L118-L137
        for repeat in range(self.repeats):
            is_reverse = repeat % 2 == 1

            repeat_start_time = self.start_time() + repeat * ms_per_repeat
            x_pos, y_pos = self.gen_points[-1] if is_reverse else self.gen_points[0]
            self.tdata.append([ x_pos, y_pos, repeat_start_time ])

            if is_reverse:
                self.tdata.extend([ *pos, repeat_start_time + (ms_per_repeat - time) ] for pos, time in reversed(ticks))
            else:
                self.tdata.extend([ *pos, repeat_start_time + time ] for pos, time in ticks)

        midpoint_time = (self.start_time() + self.end_time()) / 2
        end_tick_time = max(
            self.end_time() - StdHoldNoteHitobjectBase.END_TICK_OFFSET_MS,
            midpoint_time
        )
        x_pos, y_pos = self.time_to_pos(end_tick_time)
        self.tdata.append([ x_pos, y_pos, end_tick_time ])


    def time_to_pos(self, time):
        return self.__dist_to_pos(self.__time_to_dist(time))


    def __time_to_dist(self, time):
        percent = value_to_percent(self.start_time(), self.end_time(), time)
        return self.px_len * triangle(percent * self.repeats, 2)


    def __dist_to_pos(self, distance):
        idx = binary_search(self.length_sums, distance)
        if idx == 0: return self.gen_points[0]
        if idx == len(self.gen_points): return self.gen_points[-1]

        # avoid division by zero
        if abs(self.length_sums[idx] - self.length_sums[idx - 1]) < StdHoldNoteHitobjectBase.PRECISION_THRESHOLD_PX:
            return self.gen_points[idx]

        portion = value_to_percent(self.length_sums[idx - 1], self.length_sums[idx], distance)
        return list(map(lerp, self.gen_points[idx - 1], self.gen_points[idx], [ portion, portion ]))


    def __process_slider_data(self, sdata):
        slider_data = sdata.split('|')
        curve_type = slider_data[0].strip()

        # The first actual point is the slider's starting position, followed by all other read points
        curve_points = [ [ self.pos_x(), self.pos_y() ] ]

        for curve_data in slider_data[1:]:
            curve_data = curve_data.split(':')
            curve_points.append([ int(curve_data[0]), int(curve_data[1]) ])

        return curve_type, curve_points

    
    @staticmethod
    def __process_curve_points(curve_type, curve_points, px_len):
        if curve_type == StdHoldNoteHitobjectBase.BEZIER:
            return StdHoldNoteHitobjectBase.__make_bezier(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.CIRCUMSCRIBED:
            if len(curve_points) == 3:
                return StdHoldNoteHitobjectBase.__make_circumscribed(curve_points, px_len)
            return StdHoldNoteHitobjectBase.__make_bezier(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.LINEAR1:
            return StdHoldNoteHitobjectBase.__make_linear(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.LINEAR2:
            print('WARN[beatmap_reader]: found catmull, treating as linear')
            return StdHoldNoteHitobjectBase.__make_linear(curve_points)


    @staticmethod
    def __calculate_length_sums(gen_points):
        length_sums = [ 0 ]
        for i in range(len(gen_points) - 1):
            distance = dist(gen_points[i], gen_points[i + 1])
            length_sums.append(length_sums[-1] + distance)
        return length_sums


    @staticmethod
    def __snap_path_length(gen_points, length_sums, px_len, extend):
        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderPath.cs#L295-L303
        while length_sums[-1] > px_len:
            length_sums.pop()
            gen_points.pop()

        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderPath.cs#L314-L317
        if extend and len(gen_points) >= 2 and length_sums[-1] < px_len:
            i = 2
            # our curve generation can output repeated points, skip them
            while length_sums[-1] - length_sums[-i] < StdHoldNoteHitobjectBase.PRECISION_THRESHOLD_PX:
                if i == len(gen_points):
                    print('WARN[beatmap_reader]: slider extension failed (too short)')
                    return
                i += 1
            ratio = (px_len - length_sums[-i]) / (length_sums[-1] - length_sums[-i])
            gen_points[-1] = list(map(lerp, gen_points[-i], gen_points[-1], [ ratio, ratio ]))


    @staticmethod
    def __make_linear(curve_points):
        gen_points = []

        # Lines: generate a new curve for each sequential pair
        # ab  bc  cd  de  ef  fg
        for i in range(len(curve_points) - 1):
            bezier = Bezier([ curve_points[i], curve_points[i + 1] ])
            gen_points += bezier.curve_points
            
        return gen_points


    @staticmethod
    def __make_bezier(curve_points):
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


    @staticmethod
    def __make_circumscribed(curve_points, px_len):
        # use np.array for pointwise arithmetic
        start = np.asarray(curve_points[0])
        mid   = np.asarray(curve_points[1])
        end   = np.asarray(curve_points[2])

        # fallback to bezier in degenerate cases
        # https://github.com/ppy/osu-framework/blob/050a0b8639c9bd723100288a53923547ce87d487/osu.Framework/Utils/PathApproximator.cs#L324
        outer = (mid[1] - start[1]) * (end[0] - start[0]) - (mid[0] - start[0]) * (end[1] - start[1])
        if abs(outer) < StdHoldNoteHitobjectBase.PRECISION_THRESHOLD_PX:
            return StdHoldNoteHitobjectBase.__make_bezier(curve_points)

        def rot90acw(p):
            return np.asarray([ -p[1], p[0] ])

        # find the circle center
        mida = (start + mid)/2
        midb = (end + mid)/2
        nora = rot90acw(mid - start)
        norb = rot90acw(mid - end)
        center = intersect(
            mida, nora, midb, norb,
            precision=StdHoldNoteHitobjectBase.ARC_PARALLEL_THRESHOLD
        )
        if center is None:  # should be impossible after degeneracy check
            print('WARN[beatmap_reader]: circle center not found')
            return StdHoldNoteHitobjectBase.__make_bezier(curve_points)

        # find the orientation
        angle_sign = np.sign(np.dot(rot90acw(end - start), start - mid))
        if angle_sign == 0:  # should be impossible after degeneracy check
            print('WARN[beatmap_reader]: uncaught degenerate circle')
            return StdHoldNoteHitobjectBase.__make_linear([ start, end ])  # mid must be collinear

        # find the exact angle range
        relative_start = start - center
        start_angle = math.atan2(relative_start[1], relative_start[0])
        radius = np.linalg.norm(relative_start)
        angle_size = px_len / radius
        angle_delta = angle_sign * angle_size

        # calculate points
        steps = int(px_len / StdHoldNoteHitobjectBase.CURVE_POINTS_SEPARATION)
        step = angle_delta / steps

        def get_point(i):
            angle = start_angle + i * step
            unit = np.asarray([ math.cos(angle), math.sin(angle) ])
            return radius * unit + center

        return [ get_point(i) for i in range(steps + 1) ]

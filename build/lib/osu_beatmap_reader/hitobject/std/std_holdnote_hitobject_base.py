import math
import numpy as np

from ...utils.bezier import Bezier
from ...utils.misc import intersect, lerp, value_to_percent, binary_search, frange, catmull

from ..hitobject import Hitobject



class StdHoldNoteHitobjectBase(Hitobject):
    LINEAR_SUBDIVISIONS = 5
    CATMULL_SUBDIVISIONS = 50

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

    LINEAR        = 'L'
    CATMULL       = 'C'
    BEZIER        = 'B'
    CIRCUMSCRIBED = 'P'

    def __init__(self, **kargs):
        Hitobject.__init__(self, **kargs)

        curve_type, curve_points = self.__process_slider_data(kargs['sdata'])
        
        self.gen_points = []
        self.length_sums = []
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

        # The rough generated slider curve
        self.gen_points = StdHoldNoteHitobjectBase.__process_curve_points(self.curve_type, self.curve_points, self.px_len)
        self.length_sums = StdHoldNoteHitobjectBase.__get_length_sums(self.gen_points)
        self.__process_curve_length()

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
        start, end = self.start_time(), self.end_time()
        percent = (time - start) / (end - start)
        return self.px_len * abs(math.fmod(self.repeats * percent + 1, 2) - 1)


    def __dist_to_pos(self, distance):
        idx = binary_search(self.length_sums, distance)

        if idx == 0:
            return self.gen_points[0]
            
        if idx == len(self.gen_points):
            return self.gen_points[-1]

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
            return StdHoldNoteHitobjectBase.__make_bezier(curve_points, px_len)

        if curve_type == StdHoldNoteHitobjectBase.CIRCUMSCRIBED:
            if len(curve_points) == 3:
                return StdHoldNoteHitobjectBase.__make_circumscribed(curve_points)
            return StdHoldNoteHitobjectBase.__make_bezier(curve_points, px_len)

        if curve_type == StdHoldNoteHitobjectBase.LINEAR:
            return StdHoldNoteHitobjectBase.__make_linear(curve_points)

        if curve_type == StdHoldNoteHitobjectBase.CATMULL:
            return StdHoldNoteHitobjectBase.__make_catmull(curve_points)

        print(f'WARN[beatmap_reader]: unrecognized curve type {curve_type}')
        return []


    @staticmethod
    def __get_length_sums(gen_points):
        diffs = np.subtract(gen_points[1:], gen_points[:-1])
        length_sums = np.cumsum(np.sqrt(np.einsum('...i,...i', diffs, diffs)))
        return np.concatenate(([ 0 ], length_sums))


    def __process_curve_length(self):
        """
        Truncates and extends the curve to match the given length, and updates
        the length sums correspondingly.
        """
        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderPath.cs#L295-L303
        while self.length_sums[-1] > self.px_len:
            self.length_sums = self.length_sums[:-1]
            self.gen_points = self.gen_points[:-1]

        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderPath.cs#L284
        extend = len(self.curve_points) >= 2 and self.curve_points[-1] != self.curve_points[-2]
        
        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/SliderPath.cs#L314-L317
        if extend and len(self.gen_points) >= 2 and self.length_sums[-1] < self.px_len:
            i = 2
            
            # our curve generation can output repeated points, skip them
            while self.length_sums[-1] - self.length_sums[-i] < StdHoldNoteHitobjectBase.PRECISION_THRESHOLD_PX:
                if i == len(self.gen_points):
                    print('WARN[beatmap_reader]: slider extension failed (too short)')
                    return

                i += 1
            
            ratio = (self.px_len - self.length_sums[-i]) / (self.length_sums[-1] - self.length_sums[-i])
            self.gen_points[-1] = list(map(lerp, self.gen_points[-i], self.gen_points[-1], [ ratio, ratio ]))
            self.length_sums[-1] = self.px_len


    @staticmethod
    def __make_linear(curve_points):
        # __dist_to_pos lerps already, but subdivide so that truncation works
        return np.concatenate([
            np.linspace(curr, nxt, StdHoldNoteHitobjectBase.LINEAR_SUBDIVISIONS)
            for curr, nxt in zip(curve_points, curve_points[1:])
        ])


    @staticmethod
    def __make_catmull(curve_points):
        # https://github.com/ppy/osu-framework/blob/050a0b8639c9bd723100288a53923547ce87d487/osu.Framework/Utils/PathApproximator.cs#L142
        curve_points = list(map(np.asarray, curve_points))
        curve_points = curve_points[0:1] + curve_points
        curve_points.append(2 * curve_points[-1] - curve_points[-2])
        curve_points.append(2 * curve_points[-1] - curve_points[-2])

        t = np.linspace(0, 1, StdHoldNoteHitobjectBase.CATMULL_SUBDIVISIONS)
        t = np.expand_dims(t, -1)
        return np.concatenate([
            catmull(curve_points[i:i+4], t)
            for i in range(0, len(curve_points) - 3)
        ])


    @staticmethod
    def __make_bezier(curve_points, px_len):
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
                gen_points.extend(Bezier(point_section, length_bound=px_len).curve_points)
                point_section = []

        return gen_points


    @staticmethod
    def __make_circumscribed(curve_points):
        # use np.array for pointwise arithmetic
        start = np.asarray(curve_points[0])
        mid   = np.asarray(curve_points[1])
        end   = np.asarray(curve_points[2])

        # fallback to linear in degenerate cases
        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/Legacy/ConvertHitObjectParser.cs#L318-L322
        # https://github.com/ppy/osu/blob/ed992eed64b30209381f040586b0e8392d1c168e/osu.Game/Rulesets/Objects/Legacy/ConvertHitObjectParser.cs#L366
        outer = (mid[1] - start[1]) * (end[0] - start[0]) - (mid[0] - start[0]) * (end[1] - start[1])
        if abs(outer) < StdHoldNoteHitobjectBase.PRECISION_THRESHOLD_PX:
            return StdHoldNoteHitobjectBase.__make_linear(curve_points)

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

        # should be impossible after degeneracy check
        if center is None:
            print('WARN[beatmap_reader]: circle center not found')
            return StdHoldNoteHitobjectBase.__make_linear(curve_points)

        # find the orientation
        angle_sign = np.sign(np.dot(rot90acw(end - start), start - mid))

        # should be impossible after degeneracy check
        if angle_sign == 0:
            print('WARN[beatmap_reader]: uncaught degenerate circle')
            return StdHoldNoteHitobjectBase.__make_linear(curve_points)

        # find the exact angle range
        relative_start = start - center
        relative_end = end - center
        start_angle = math.atan2(relative_start[1], relative_start[0])
        end_angle = math.atan2(relative_end[1], relative_end[0])
        radius = np.linalg.norm(relative_start)

        angle_size = angle_sign * (end_angle - start_angle)

        if angle_size < 0:
            angle_size += 2 * math.pi

        if angle_size > 2 * math.pi:
            angle_size -= 2 * math.pi

        angle_delta = angle_sign * angle_size

        # calculate points
        steps = int(radius * angle_size / StdHoldNoteHitobjectBase.CURVE_POINTS_SEPARATION) + 2
        angles = np.linspace(start_angle, start_angle + angle_delta, steps)
        return np.add(center, radius * np.transpose([ np.cos(angles), np.sin(angles) ]))

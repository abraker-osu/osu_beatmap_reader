import numpy as np

from osu_interfaces import IBeatmap

from .gamemode import Gamemode
from .hitobject import Hitobject


class BeatmapBase(IBeatmap):

    class Metadata():

        def __init__(self):
            IBeatmap.Metadata.__init__(self)

            self.beatmap_format = -1    # *.osu format
            self.artist         = ''
            self.title          = ''
            self.version        = ''    # difficulty name
            self.creator        = ''
            self.name           = ''    # Artist - Title (Creator) [Difficulty]

            self.beatmap_id     = ''
            self.beatmapset_id  = ''
            self.beatmap_md5    = ''  # generatedilepath:

    class Difficulty():

        def __init__(self):
            IBeatmap.Difficulty.__init__(self)
            self.hp = None
            self.cs = None
            self.od = None
            self.ar = None
            self.sm = None
            self.st = None


    class TimingPoint():

        def __init__(self):
            self.offset = 0
            self.beat_interval = 0
            self.inherited:         bool
            self.meter:             int

            self.beat_length:       float
            self.bpm:               float
            self.slider_multiplier: float


    def __init__(self):
        self.metadata   = BeatmapBase.Metadata()
        self.difficulty = BeatmapBase.Difficulty()
        self.gamemode   = Gamemode(Gamemode.OSU)

        self.timing_points:     list[BeatmapBase.TimingPoint] = []
        self.hitobjects:        list[Hitobject]               = []
        self.end_times:         list[int]                     = []
        self.slider_tick_times: list[int]                     = []

        self.bpm_min = float('inf')
        self.bpm_max = float('-inf')


    def data(self) -> np.ndarray:
        data = []
        timing_shape = np.shape(self.hitobjects[0].tick_data())[1] + 1

        for i, hitobject in zip(range(len(self.hitobjects)), self.hitobjects):
            timing = np.zeros(timing_shape)
            for tick in hitobject.tick_data():
                timing[0] = i
                timing[1:] = tick
                data.append(timing)

        return np.asarray(data)


    def get_diff_data(self) -> Difficulty:
        return self.difficulty


    def get_hitobjects(self) -> list:
        return self.hitobjects


    def set_cs(self, cs: float):
        if self.gamemode == Gamemode.MANIA:
            if not 0 <= cs <= 18:
                raise ValueError(f'CS must be between 0 and 10, inclusive! CS = {cs}')
        else:
            if not 0 <= cs <= 10:
                raise ValueError(f'CS must be between 0 and 10, inclusive! CS = {cs}')

        self.difficulty.cs = float(cs)


    def set_ar(self, ar: float):
        if not 0 <= ar <= 10:
            raise ValueError(f'AR must be between 0 and 10, inclusive! AR = {ar}')
        self.difficulty.ar = float(ar)


    def set_od(self, od: float):
        if not 0 <= od <= 10:
            raise ValueError(f'OD must be between 0 and 10, inclusive! OD = {od}')
        self.difficulty.od = float(od)


    def set_hp(self, hp: float):
        if not 0 <= hp <= 10:
            raise ValueError(f'HP must be between 0 and 10, inclusive! HP = {hp}')
        self.difficulty.hp = float(hp)


    def set_sm(self, sm: float):
        self.difficulty.sm = float(sm)


    def set_st(self, st: float):
        self.difficulty.st = float(st)

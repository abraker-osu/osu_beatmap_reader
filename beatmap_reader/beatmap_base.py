import numpy as np
import math

from osu_interfaces import IBeatmap
from .gamemode import Gamemode


class BeatmapBase(IBeatmap):

    PLAYFIELD_WIDTH  = 512  # osu!px
    PLAYFIELD_HEIGHT = 384  # osu!px

    class Metadata():

        def __init__(self):
            self.beatmap_format = -1    # *.osu format
            self.artist         = ''
            self.title          = ''
            self.version        = ''    # difficulty name
            self.creator        = ''
            self.name           = ''    # Artist - Title (Creator) [Difficulty]
            
            self.beatmap_id     = None
            self.beatmapset_id  = None
            self.beatmap_md5    = None  # generatedilepath:

    
    class TimingPoint():

        def __init__(self):
            self.offset        = None
            self.beat_interval = None
            self.inherited     = None
            self.meter         = None

            self.beat_length       = None
            self.bpm               = None
            self.slider_multiplier = None


    class Difficulty():

        def __init__(self):
            self.hp = None
            self.cs = None
            self.od = None
            self.ar = None
            self.sm = None
            self.st = None


    def __init__(self):
        self.metadata   = BeatmapBase.Metadata()
        self.difficulty = BeatmapBase.Difficulty()
        self.gamemode   = None
        
        self.timing_points     = []
        self.hitobjects        = []
        self.end_times         = []
        self.slider_tick_times = []

        self.bpm_min = float('inf')
        self.bpm_max = float('-inf')


    def data(self):
        data = []
        timing_shape = np.shape(self.hitobjects[0].tick_data())[1] + 1

        for i, hitobject in zip(range(len(self.hitobjects)), self.hitobjects):
            timing = np.zeros(timing_shape)
            for tick in hitobject.tick_data():
                timing[0] = i
                timing[1:] = tick
                data.append(timing)
        
        return np.asarray(data)


    def get_diff_data(self):
        return self.difficulty


    def get_hitobjects(self):
        return self.hitobjects


    def set_cs(self, cs):
        if not 0 <= cs <= 10:
            raise ValueError(f'CS must be between 0 and 10, inclusive! CS = {cs}')
        self.difficulty.cs = float(cs)


    def set_ar(self, ar):
        if not 0 <= ar <= 10:
            raise ValueError(f'AR must be between 0 and 10, inclusive! AR = {ar}')
        self.difficulty.ar = float(ar)


    def set_od(self, od):
        if not 0 <= od <= 10:
            raise ValueError(f'OD must be between 0 and 10, inclusive! OD = {od}')
        self.difficulty.od = float(od)


    def set_hp(self, hp):
        if not 0 <= hp <= 10:
            raise ValueError(f'HP must be between 0 and 10, inclusive! HP = {hp}')
        self.difficulty.hp = float(hp)


    def set_sm(self, sm):
        self.difficulty.sm = float(sm)


    def set_st(self, st):
        self.difficulty.st = float(st)
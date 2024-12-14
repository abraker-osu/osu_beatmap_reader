import math

from ..hitobject import Hitobject
from ...beatmap_base import BeatmapBase



class ManiaSingleNoteHitobjectBase(Hitobject):

    def __init__(self, **kargs):
        Hitobject.__init__(self, **kargs)

        ratio = kargs['keys'] / BeatmapBase.PLAYFIELD_WIDTH   # columns per osu!px
        self.hdata[Hitobject.HDATA_POSX] = min(math.floor(ratio*self.pos_x()), kargs['keys'] - 1)


    def generate_tick_data(self, **kargs):
        self.tdata = [
            [ self.pos_x(),  self.start_time() ],
            [ self.pos_x(),  self.end_time() ],
        ]
from ..hitobject import Hitobject


class StdSpinnerHitobjectBase(Hitobject):

    def __init__(self, beatmap=None):
        self.beatmap  = beatmap
        self.end_time = None

        Hitobject.__init__(self)

    
    def get_end_time(self):
        return self.end_time
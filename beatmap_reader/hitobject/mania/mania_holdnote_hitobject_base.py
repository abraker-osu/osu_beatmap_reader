from ..hitobject import Hitobject



class ManiaHoldNoteHitobjectBase(Hitobject):

    def __init__(self):
        self.end_time = None
        Hitobject.__init__(self)
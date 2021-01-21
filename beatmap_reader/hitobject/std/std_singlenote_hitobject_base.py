from ..hitobject import Hitobject



class StdSingleNoteHitobjectBase(Hitobject):

    def __init__(self):
        Hitobject.__init__(self)


    def time_to_pos(self, time):
        return self.pos
        

    def get_aimpoint_times(self):
        return [ self.time ]
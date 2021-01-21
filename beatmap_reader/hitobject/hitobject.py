
"""
Abstract object that holds common hitobject data

Input: 
    beatmap_data - hitobject data read from the beatmap file
"""
class Hitobject():

    CIRCLE  = 1 << 0
    SLIDER  = 1 << 1
    NCOMBO  = 1 << 2
    SPINNER = 1 << 3
    # ???
    MANIALONG = 1 << 7

    def __init__(self):

        self.hitobject_type = None
        self.start_time     = None
        self.end_time       = None
        self.index          = None
        self.pos            = None


    def get_end_time(self):
        return self.end_time


    def is_hitobject_type(self, hitobject_type):
        return (self.hitobject_type & hitobject_type) > 0


    def is_hitobject_long(self):
        return self.is_hitobject_type(Hitobject.SLIDER) or self.is_hitobject_type(Hitobject.MANIALONG)
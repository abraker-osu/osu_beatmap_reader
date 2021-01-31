import numpy as np

from ..osu_interfaces.IHitobject import IHitobject


"""
Abstract object that holds common hitobject data

Input: 
    beatmap_data - hitobject data read from the beatmap file
"""
class Hitobject(IHitobject):

    CIRCLE  = 1 << 0
    SLIDER  = 1 << 1
    NCOMBO  = 1 << 2
    SPINNER = 1 << 3
    # ???
    MANIALONG = 1 << 7

    HDATA_POSX = 0   # Hitobject x position
    HDATA_POSY = 1   # Hitobject y position
    HDATA_TSRT = 2   # Hitobject start time
    HDATA_TEND = 3   # Hitobject end time
    HDATA_TYPE = 4   # Hitobject type

    TDATA_X = 0      # Tick x position
    TDATA_Y = 1      # Tick y positon
    TDATA_T = 2      # Tick time

    def __init__(self, **kargs):
        # Basic details every hitobject has, indexed by HDATA
        self.hdata = [ None, None, None, None, None ]

        # Tick data are points along long hitobject, indexed by TDATA
        self.tdata = []

        # Fill in data
        if kargs['htype'] & Hitobject.CIRCLE:
            self.hdata = [ kargs['posx'], kargs['posy'], kargs['tstart'], kargs['tstart'] + 1, kargs['htype'] ]
            return

        if kargs['htype'] & Hitobject.SLIDER:
            self.hdata = [ kargs['posx'], kargs['posy'], kargs['tstart'], None, kargs['htype'] ]
            return

        if kargs['htype'] & Hitobject.SPINNER:
            self.hdata = [ kargs['posx'], kargs['posy'], kargs['tstart'], kargs['tend'], kargs['htype'] ]
            return

        if kargs['htype'] & Hitobject.MANIALONG:
            self.hdata = [ kargs['posx'], kargs['posy'], kargs['tstart'], None, kargs['htype'] ]
            return

        self.index = None


    def __repr__(self):
        return str(self.tick_data())


    def pos_x(self):
        return self.hdata[Hitobject.HDATA_POSX]


    def pos_y(self):
        return self.hdata[Hitobject.HDATA_POSY]


    def start_time(self):
        return self.hdata[Hitobject.HDATA_TSRT]


    def end_time(self):
        return self.hdata[Hitobject.HDATA_TEND]


    def tick_data(self):
        return np.asarray(self.tdata)


    def is_htype(self, hitobject_type):
        return (self.hdata[Hitobject.HDATA_TYPE] & hitobject_type) > 0


    def is_hlong(self):
        return self.is_htype(Hitobject.SLIDER) or self.is_htype(Hitobject.MANIALONG)


    def generate_tick_data(self, **kargs):
        raise NotImplementedError('')
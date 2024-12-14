import numpy as np

from osu_interfaces import IHitobject


class Hitobject(IHitobject):
    """
    Abstract object that holds common hitobject data

    Input:
        beatmap_data - hitobject data read from the beatmap file
    """

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
        self.hdata: list[int | None] = [ None, None, None, None, None ]

        # Tick data are points along long hitobject, indexed by TDATA
        self.tdata = []

        # Number of repeats. Used for sliders
        self.repeats = 0

        self.px_len = 0

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


    def __repr__(self) -> str:
        return str(self.tick_data())


    def pos_x(self) -> int:
        ret = self.hdata[Hitobject.HDATA_POSX]
        if ret is None:
            raise ValueError('Hitobject pos_x is None')

        return ret


    def pos_y(self) -> int:
        ret = self.hdata[Hitobject.HDATA_POSY]
        if ret is None:
            raise ValueError('Hitobject pos_y is None')

        return ret


    def start_time(self) -> int:
        ret = self.hdata[Hitobject.HDATA_TSRT]
        if ret is None:
            raise ValueError('Hitobject start_time is None')

        return ret


    def end_time(self) -> int:
        ret = self.hdata[Hitobject.HDATA_TEND]
        if ret is None:
            raise ValueError('Hitobject end_time is None')

        return ret


    def tick_data(self) -> np.ndarray:
        return np.asarray(self.tdata)


    def is_htype(self, hitobject_type: int) -> bool:
        htype = self.hdata[Hitobject.HDATA_TYPE]
        if htype is None:
            raise ValueError('Hitobject type is None')

        return ( htype & hitobject_type ) > 0


    def is_hlong(self) -> bool:
        return self.is_htype(Hitobject.SLIDER) or self.is_htype(Hitobject.MANIALONG)


    def generate_tick_data(self, **kargs):
        raise NotImplementedError('')

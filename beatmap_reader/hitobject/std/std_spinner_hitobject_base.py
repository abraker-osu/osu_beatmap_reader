from ..hitobject import Hitobject


class StdSpinnerHitobjectBase(Hitobject):

    def __init__(self, **kargs):
        Hitobject.__init__(self, **kargs)

    
    def generate_tick_data(self, **kargs):
        self.tdata = [
            [ self.pos_x(), self.pos_y(), self.start_time() ],
            [ self.pos_x(), self.pos_y(), self.end_time() ],
        ]
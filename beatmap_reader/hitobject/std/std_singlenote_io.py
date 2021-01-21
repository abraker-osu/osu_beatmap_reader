import math

from .std_singlenote_hitobject_base import StdSingleNoteHitobjectBase


class StdSingleNoteIO():

    @staticmethod
    def load_singlenote(data, difficulty):
        singlenote = StdSingleNoteHitobjectBase()
        if not data: return singlenote

        StdSingleNoteIO.__process_hitobject_data(data, singlenote, difficulty)

        return singlenote


    @staticmethod
    def get_data(self, singlenote):
        # TODO
        pass


    @staticmethod
    def __process_hitobject_data(data, singlenote, difficulty):
        singlenote.pos            = [ int(data[0]), int(data[1]) ]
        singlenote.time           = int(data[2])
        singlenote.hitobject_type = int(data[3])

        singlenote.difficulty     = difficulty
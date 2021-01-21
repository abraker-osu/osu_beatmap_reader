import math

from .std_spinner_hitobject_base import StdSpinnerHitobjectBase


class StdSpinnerIO():

    @staticmethod
    def load_spinner(data, difficulty):
        spinner = StdSpinnerHitobjectBase()
        if not data: return spinner

        StdSpinnerIO.__process_hitobject_data(data, spinner, difficulty)

        return spinner


    @staticmethod
    def get_data(self, spinner):
        # TODO
        pass


    @staticmethod
    def __process_hitobject_data(data, spinner, difficulty):
        spinner.pos            = [ int(data[0]), int(data[1]) ]
        spinner.time           = int(data[2])
        spinner.hitobject_type = int(data[3])
        spinner.end_time       = int(data[5])

        spinner.difficulty     = difficulty
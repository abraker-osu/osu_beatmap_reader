import unittest
import os
import json
import timeit

from numpy.lib.nanfunctions import nancumsum

from ..utils.bezier import Bezier

from ..beatmapIO import BeatmapIO
from ..hitobject.hitobject import Hitobject
from ..hitobject.std.std_holdnote_hitobject_base import StdHoldNoteHitobjectBase


class TestBeatmap(unittest.TestCase):

    '''
    def test_beatmap_loading_mania(self):
        beatmap = BeatmapIO.open_beatmap(os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'mania', 'Camellia - GHOST (qqqant) [Collab PHANTASM [MX]].osu'
        ))
        
        # Test metadata
        self.assertEqual(beatmap.metadata.beatmap_format, 14)
        self.assertEqual(beatmap.metadata.title, 'GHOST')
        self.assertEqual(beatmap.metadata.artist, 'Camellia')
        self.assertEqual(beatmap.metadata.version, 'Collab PHANTASM [MX]')
        self.assertEqual(beatmap.metadata.creator, 'qqqant')

        # Test timing points
        self.assertEqual(len(beatmap.timing_points), 179)

        self.assertEqual(beatmap.timing_points[0].offset, 8527)
        self.assertEqual(beatmap.timing_points[0].beat_interval, 272.727272727273)
        self.assertEqual(beatmap.timing_points[0].meter, 4)
        self.assertEqual(beatmap.timing_points[0].inherited, False)

        self.assertEqual(beatmap.timing_points[178].offset, 316163)
        self.assertEqual(beatmap.timing_points[178].beat_interval, -125)
        self.assertEqual(beatmap.timing_points[178].meter, 4)
        self.assertEqual(beatmap.timing_points[178].inherited, True)

        # Test hitobjects
        self.assertEqual(max(beatmap.data()[:, 1]), 3)
        self.assertEqual(len(beatmap.data())/2, 3004)

        # TODO: test hitobjects


    def test_beatmap_loading_std(self):
        beatmap = BeatmapIO.open_beatmap(os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'Mutsuhiko Izumi - Red Goose (nold_1702) [ERT Basic].osu'
        ))

        # Test metadata
        self.assertEqual(beatmap.metadata.beatmap_format, 9)
        self.assertEqual(beatmap.metadata.title, 'Red Goose')
        self.assertEqual(beatmap.metadata.artist, 'Mutsuhiko Izumi')
        self.assertEqual(beatmap.metadata.version, 'ERT Basic')
        self.assertEqual(beatmap.metadata.creator, 'nold_1702')

        # Test timing points
        self.assertEqual(len(beatmap.timing_points), 23)

        self.assertEqual(beatmap.timing_points[0].offset, -401)
        self.assertEqual(beatmap.timing_points[0].beat_interval, 300)
        self.assertEqual(beatmap.timing_points[0].meter, 4)
        self.assertEqual(beatmap.timing_points[0].inherited, False)


        self.assertEqual(beatmap.timing_points[22].offset, 117799)
        self.assertEqual(beatmap.timing_points[22].beat_interval, -100)
        self.assertEqual(beatmap.timing_points[22].meter, 4)
        self.assertEqual(beatmap.timing_points[22].inherited, True)

        # Test hitobjects
        self.assertEqual(len(beatmap.hitobjects), 102)

        self.assertTrue(beatmap.hitobjects[-1].is_htype(Hitobject.SPINNER))
        self.assertEqual(beatmap.hitobjects[-1].hdata[Hitobject.HDATA_TSRT], 114649)
        self.assertEqual(beatmap.hitobjects[-1].hdata[Hitobject.HDATA_TEND], 117799)

        self.assertTrue(beatmap.hitobjects[16].is_htype(Hitobject.CIRCLE))
        self.assertEqual(beatmap.hitobjects[16].hdata[Hitobject.HDATA_TSRT], 24499)
        self.assertEqual(beatmap.hitobjects[16].hdata[Hitobject.HDATA_POSX], 208)
        self.assertEqual(beatmap.hitobjects[16].hdata[Hitobject.HDATA_POSY], 84)

        self.assertTrue(beatmap.hitobjects[23].is_htype(Hitobject.SLIDER))
        self.assertEqual(beatmap.hitobjects[23].hdata[Hitobject.HDATA_TSRT], 28399)
        self.assertEqual(beatmap.hitobjects[23].hdata[Hitobject.HDATA_TEND], 29299)
        self.assertEqual(beatmap.hitobjects[23].hdata[Hitobject.HDATA_POSX], 172)
        self.assertEqual(beatmap.hitobjects[23].hdata[Hitobject.HDATA_POSY], 116)
        self.assertEqual(beatmap.hitobjects[23].repeats, 2)
        self.assertEqual(len(beatmap.hitobjects[23].tdata), 5)
        # head
        self.assertEqual(beatmap.hitobjects[23].tdata[0][Hitobject.TDATA_T], 28399)
        self.assertEqual(beatmap.hitobjects[23].tdata[0][Hitobject.TDATA_X], 172)
        self.assertEqual(beatmap.hitobjects[23].tdata[0][Hitobject.TDATA_Y], 116)
        # tick
        self.assertAlmostEqual(beatmap.hitobjects[23].tdata[1][Hitobject.TDATA_T], 28699, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[1][Hitobject.TDATA_X], 207, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[1][Hitobject.TDATA_Y], 48, places=0)
        # repeat
        self.assertAlmostEqual(beatmap.hitobjects[23].tdata[2][Hitobject.TDATA_T], 28849, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[2][Hitobject.TDATA_X], 241, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[2][Hitobject.TDATA_Y], 28, places=0)
        # tick
        self.assertAlmostEqual(beatmap.hitobjects[23].tdata[3][Hitobject.TDATA_T], 28999, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[3][Hitobject.TDATA_X], 207, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[3][Hitobject.TDATA_Y], 48, places=0)
        # end
        self.assertAlmostEqual(beatmap.hitobjects[23].tdata[4][Hitobject.TDATA_T], 29263, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[4][Hitobject.TDATA_X], 175, places=0)
        self.assertAlmostEquals(beatmap.hitobjects[23].tdata[4][Hitobject.TDATA_Y], 107, places=0)


    def test_beatmap_loading_weird(self):
        beatmap = BeatmapIO.open_beatmap(os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'stargazer.osu'
        ))

        circular = beatmap.hitobjects[0]
        self.assertTrue(circular.is_htype(Hitobject.SLIDER))
        self.assertEqual(len(circular.tdata), 6)  # head + 4 ticks + end
        self.assertEqual(circular.hdata[Hitobject.HDATA_TSRT], 343)
        self.assertEqual(circular.hdata[Hitobject.HDATA_POSX], 168)
        self.assertEqual(circular.hdata[Hitobject.HDATA_POSY], 83)
        # tick 1
        self.assertAlmostEqual(circular.tdata[1][Hitobject.TDATA_T], 700, places=0)
        self.assertAlmostEqual(circular.tdata[1][Hitobject.TDATA_X], 114, places=0)
        self.assertAlmostEqual(circular.tdata[1][Hitobject.TDATA_Y], 216, places=0)
        # tick 4
        self.assertAlmostEqual(circular.tdata[4][Hitobject.TDATA_T], 1772, places=0)
        self.assertAlmostEqual(circular.tdata[4][Hitobject.TDATA_X], 397, places=0)
        self.assertAlmostEqual(circular.tdata[4][Hitobject.TDATA_Y], 176, places=0)
        # end
        self.assertAlmostEqual(circular.tdata[5][Hitobject.TDATA_T], 2003, places=0)
        self.assertAlmostEqual(circular.tdata[5][Hitobject.TDATA_X], 352, places=0)
        self.assertAlmostEqual(circular.tdata[5][Hitobject.TDATA_Y], 91, places=0)

        distorted = next(h for h in beatmap.hitobjects if h.start_time() == 85699)
        self.assertEqual(distorted.hdata[Hitobject.HDATA_POSX], 360)
        self.assertEqual(distorted.hdata[Hitobject.HDATA_POSY], 272)
        self.assertEqual(len(distorted.tdata), 1)
        self.assertEqual(distorted.tdata[0][Hitobject.TDATA_T], 85699)
        self.assertEqual(distorted.tdata[0][Hitobject.TDATA_X], 360)
        self.assertEqual(distorted.tdata[0][Hitobject.TDATA_Y], 272)
    

    def test_beatmap_loading_slider_ticks(self):
        beatmap = BeatmapIO.open_beatmap(os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'abraker - unknown (abraker) [slider_test].osu'
        ))
        data_path = os.path.join(
            'beatmap_reader', 'unit_tests', 'data', 'slider_test_data.json'
        )
        with open(data_path, 'r') as f:
            data = json.loads(f.read())
        for i, tdata in data.items():
            object = beatmap.hitobjects[int(i)]
            int_data = [ list(map(int, tick)) for tick in object.tdata ]
            self.assertEqual(int_data, tdata)
    

    def test_beatmap_loading_custom(self):
        beatmap = BeatmapIO.open_beatmap(os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'abraker - unknown (abraker) [250ms].osu'
        ))
    '''


    def test_performance(self):
        '''
        n = 10

        path = os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'abraker - unknown (abraker) [slider_test].osu'
        )
        print(path, timeit.Timer(lambda: BeatmapIO.open_beatmap(path)).timeit(number=n)/n)

        path = os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'Mutsuhiko Izumi - Red Goose (nold_1702) [ERT Basic].osu'
        )
        print(path, timeit.Timer(lambda:  BeatmapIO.open_beatmap(path)).timeit(number=n)/n)
        '''
        path = os.path.join(
            'beatmap_reader', 'unit_tests', 'maps',
            'osu', 'stargazer.osu'
        )
        print(path, timeit.Timer(lambda: BeatmapIO.open_beatmap(path)).timeit(number=1))

    
    '''
    def test_slider_performance(self):
        n = 10
        data_path = os.path.join(
            'beatmap_reader', 'unit_tests', 'data', 'slider_input_data.json'
        )

        with open(data_path, 'r') as f:
            data = json.loads(f.read())

        for i, slider_data in data.items():
            print(f'Hitobject {i}: ', timeit.Timer(lambda: StdHoldNoteHitobjectBase(**slider_data)).timeit(number=n)/n)
    '''


    '''
    def test_bezier_performance(self):
        n = 10
        data_path = os.path.join(
            'beatmap_reader', 'unit_tests', 'data', 'bezier_input_data.json'
        )

        with open(data_path, 'r') as f:
            data = json.loads(f.read())

        for i, bezier_data in data.items():
            print(f'Bezier {i}: ', timeit.Timer(lambda: Bezier(bezier_data)).timeit(number=n)/n)
    '''
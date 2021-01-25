import unittest

from ..beatmapIO import BeatmapIO


class TestBeatmap(unittest.TestCase):

    def test_beatmap_loading_mania(self):
        beatmap = BeatmapIO.open_beatmap('beatmap_reader\\unit_tests\\maps\\mania\\Camellia - GHOST (qqqant) [Collab PHANTASM [MX]].osu')
        
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
        beatmap = BeatmapIO.open_beatmap('beatmap_reader\\unit_tests\\maps\\osu\\Mutsuhiko Izumi - Red Goose (nold_1702) [ERT Basic].osu')

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

        # TODO: test hitobjects
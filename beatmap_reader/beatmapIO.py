import warnings
import numpy as np

from .beatmap_base import BeatmapBase
from .gamemode import Gamemode

from .hitobject.hitobject import Hitobject

#from .hitobject.std.std_singlenote_io import StdSingleNoteIO
#from .hitobject.std.std_holdnote_io import StdHoldNoteIO
#from .hitobject.std.std_spinner_io import StdSpinnerIO

from .hitobject.std.std_singlenote_hitobject_base import StdSingleNoteHitobjectBase
from .hitobject.std.std_holdnote_hitobject_base import StdHoldNoteHitobjectBase
from .hitobject.std.std_spinner_hitobject_base import StdSpinnerHitobjectBase


#from .hitobject.taiko.taiko_singlenote_hitobject import TaikoSingleNoteHitobject
#from .hitobject.taiko.taiko_holdnote_hitobject import TaikoHoldNoteHitobject
#from .hitobject.taiko.taiko_spinner_hitobject import TaikoSpinnerHitobject

#from .hitobject.catch.catch_singlenote_hitobject import CatchSingleNoteHitobject
#from .hitobject.catch.catch_holdnote_hitobject import CatchHoldNoteHitobject
#from .hitobject.catch.catch_spinner_hitobject import CatchSpinnerHitobject

#from .hitobject.mania.mania_singlenote_io import ManiaSingleNoteIO
#from .hitobject.mania.mania_holdnote_io import ManiaHoldNoteIO

from .hitobject.mania.mania_singlenote_hitobject_base import ManiaSingleNoteHitobjectBase
from .hitobject.mania.mania_holdnote_hitobject_base import ManiaHoldNoteHitobjectBase


'''
Handles beatmap loading

Input: 
    load_beatmap - load the beatmap specified

Output: 
    metadata - information about the beatmap
    hitobjects - list of hitobjects present in the map
    timingpoints - list of timing points present in the map
'''
class BeatmapIO():

    class __Section():

        SECTION_NONE         = 0
        SECTION_GENERAL      = 1
        SECTION_EDITOR       = 2
        SECTION_METADATA     = 3
        SECTION_DIFFICULTY   = 4
        SECTION_EVENTS       = 5
        SECTION_TIMINGPOINTS = 6
        SECTION_COLOURS      = 7
        SECTION_HITOBJECTS   = 8


    class BeatmapIOException(Exception):
        pass


    @staticmethod
    def init():
        BeatmapIO.__SECTION_MAP = {
            BeatmapIO.__Section.SECTION_GENERAL      : BeatmapIO.__parse_general_section,
            BeatmapIO.__Section.SECTION_EDITOR       : BeatmapIO.__parse_editor_section,
            BeatmapIO.__Section.SECTION_METADATA     : BeatmapIO.__parse_metadata_section,
            BeatmapIO.__Section.SECTION_DIFFICULTY   : BeatmapIO.__parse_difficulty_section,
            BeatmapIO.__Section.SECTION_EVENTS       : BeatmapIO.__parse_events_section,
            BeatmapIO.__Section.SECTION_TIMINGPOINTS : BeatmapIO.__parse_timingpoints_section,
            BeatmapIO.__Section.SECTION_COLOURS      : BeatmapIO.__parse_colour_section,
            BeatmapIO.__Section.SECTION_HITOBJECTS   : BeatmapIO.__parse_hitobjects_section
        }


    """
    Opens a beatmap file and reads it

    Args:
        filepath: (string) filepath to the beatmap file to load
    """
    @staticmethod
    def open_beatmap(filepath=None):
        with open(filepath, 'rt', encoding='utf-8') as beatmap_file:
            beatmap = BeatmapIO.load_beatmap(beatmap_file)
        
        return beatmap


    """
    Loads beatmap data

    Args:
        beatmap_file: (string) contents of the beatmap file
    """
    @staticmethod
    def load_beatmap(beatmap_data):
        beatmap = BeatmapBase()
        
        # Load all the data
        BeatmapIO.__parse_beatmap_file_format(beatmap_data, beatmap)
        BeatmapIO.__parse_beatmap_content(beatmap_data, beatmap)

        # Process all the data
        BeatmapIO.__process_timing_points(beatmap)
        BeatmapIO.__postprocess_hitobjects(beatmap)

        # Fill in extra data if it's missing
        BeatmapIO.__postprocess_map(beatmap)

        return beatmap


    """
    Saves beatmap file data

    Args:
        filepath: (string) what to save the beatmap as
    """
    @staticmethod
    def save_beatmap(beatmap_data, filepath):
        with open(filepath, 'wt', encoding='utf-8') as f:
            f.write(beatmap_data)


    """
    Returns:
        MD5 checksum of the beatmap file
    """
    @staticmethod
    def get_md5(beatmap):
        pass


    @staticmethod
    def __postprocess_map(beatmap):
        if beatmap.difficulty.ar == None:
            beatmap.set_ar(beatmap.difficulty.od)

        if beatmap.difficulty.hp == None:
            beatmap.set_hp(beatmap.difficulty.od)

        if beatmap.gamemode == None:
            beatmap.gamemode = Gamemode(Gamemode.OSU)

        beatmap.metadata.name = beatmap.metadata.artist + ' - ' + beatmap.metadata.title + ' (' + beatmap.metadata.creator + ') ' + '[' + beatmap.metadata.version + ']'


    @staticmethod
    def __parse_beatmap_file_format(beatmap_data, beatmap):
        line  = beatmap_data.readline()
        data  = line.split('osu file format v')
        
        try: beatmap.metadata.beatmap_format = int(data[1])
        except: return


    @staticmethod
    def __parse_beatmap_content(beatmap_data, beatmap):
        if beatmap.metadata.beatmap_format == -1: return

        section = BeatmapIO.__Section.SECTION_NONE
        line    = ''
        
        while True:
            line = beatmap_data.readline()

            if line.strip() == '[General]':        section = BeatmapIO.__Section.SECTION_GENERAL
            elif line.strip() == '[Editor]':       section = BeatmapIO.__Section.SECTION_EDITOR
            elif line.strip() == '[Metadata]':     section = BeatmapIO.__Section.SECTION_METADATA
            elif line.strip() == '[Difficulty]':   section = BeatmapIO.__Section.SECTION_DIFFICULTY
            elif line.strip() == '[Events]':       section = BeatmapIO.__Section.SECTION_EVENTS
            elif line.strip() == '[TimingPoints]': section = BeatmapIO.__Section.SECTION_TIMINGPOINTS
            elif line.strip() == '[Colours]':      section = BeatmapIO.__Section.SECTION_COLOURS
            elif line.strip() == '[HitObjects]':   section = BeatmapIO.__Section.SECTION_HITOBJECTS
            elif line == '':               
                return
            else:
                BeatmapIO.__parse_section(section, line, beatmap)


    @staticmethod
    def __parse_section(section, line, beatmap):
        if section != BeatmapIO.__Section.SECTION_NONE:
            BeatmapIO.__SECTION_MAP[section](line, beatmap)


    @staticmethod
    def __parse_general_section(line, beatmap):
        data = line.split(':', 1)
        if len(data) < 2: return

        data[0] = data[0].strip()

        if data[0] == 'PreviewTime':
            # ignore
            return

        if data[0] == 'Countdown':
            # ignore
            return

        if data[0] == 'SampleSet':
            # ignore
            return

        if data[0] == 'StackLeniency':
            # ignore
            return

        if data[0] == 'Mode':
            beatmap.gamemode = int(data[1])
            return

        if data[0] == 'LetterboxInBreaks':
            # ignore
            return

        if data[0] == 'SpecialStyle':
            # ignore
            return

        if data[0] == 'WidescreenStoryboard':
            # ignore
            return


    @staticmethod
    def __parse_editor_section(line, beatmap):
        data = line.split(':', 1)
        if len(data) < 2: return

        if data[0] == 'DistanceSpacing':
            # ignore
            return

        if data[0] == 'BeatDivisor':
            # ignore
            return

        if data[0] == 'GridSize':
            # ignore
            return

        if data[0] == 'TimelineZoom':
            # ignore
            return


    @staticmethod
    def __parse_metadata_section(line, beatmap):
        data = line.split(':', 1)
        if len(data) < 2: return
        data[0] = data[0].strip()

        if data[0] == 'Title':
            beatmap.metadata.title = data[1].strip()
            return

        if data[0] == 'TitleUnicode':
            # ignore
            return

        if data[0] == 'Artist':
            beatmap.metadata.artist = data[1].strip()
            return

        if data[0] == 'ArtistUnicode':
            # ignore
            return

        if data[0] == 'Creator':
            beatmap.metadata.creator = data[1].strip()
            return

        if data[0] == 'Version':
            beatmap.metadata.version = data[1].strip()
            return

        if data[0] == 'Source':
            # ignore
            return

        if data[0] == 'Tags':
            # ignore
            return

        if data[0] == 'BeatmapID':
            beatmap.metadata.beatmap_id = data[1].strip()
            return

        if data[0] == 'BeatmapSetID':
            beatmap.metadata.beatmapset_id = data[1].strip()
            return


    @staticmethod
    def __parse_difficulty_section(line, beatmap):
        data = line.split(':', 1)
        if len(data) < 2: return

        data[0] = data[0].strip()

        if data[0] == 'HPDrainRate':
            beatmap.set_hp(float(data[1]))
            return

        if data[0] == 'CircleSize':
            beatmap.set_cs(float(data[1]))
            return

        if data[0] == 'OverallDifficulty':
            beatmap.set_od(float(data[1]))
            return

        if data[0] == 'ApproachRate':
            beatmap.set_ar(float(data[1]))
            return

        if data[0] == 'SliderMultiplier':
            beatmap.set_sm(float(data[1]))
            return

        if data[0] == 'SliderTickRate':
            beatmap.set_st(float(data[1]))
            return


    @staticmethod
    def __parse_events_section(line, beatmap):
        # ignore
        return


    @staticmethod
    def __parse_timingpoints_section(line, beatmap):
        data = line.split(',')
        if len(data) < 2: return

        timing_point = BeatmapBase.TimingPoint()
        
        timing_point.offset        = float(data[0])
        timing_point.beat_interval = float(data[1])

        # Old maps don't have meteres
        if len(data) > 2: timing_point.meter = int(data[2])
        else:             timing_point.meter = 4

        if len(data) > 6: timing_point.inherited = False if int(data[6]) == 1 else True
        else:             timing_point.inherited = False

        beatmap.timing_points.append(timing_point)


    @staticmethod
    def __parse_colour_section(self, line):
        # ignore
        return


    @staticmethod
    def __parse_hitobjects_section(line, beatmap):
        data = line.split(',')
        if len(data) < 2: return
        
        hitobject_type = int(data[3])

        if beatmap.gamemode == Gamemode(Gamemode.OSU) or beatmap.gamemode == None:
            if hitobject_type & Hitobject.CIRCLE > 0:
                beatmap.hitobjects.append(StdSingleNoteHitobjectBase(
                    posx   = int(data[0]), 
                    posy   = int(data[1]), 
                    tstart = int(data[2]), 
                    htype  = int(data[3]),
                ))
                return

            if hitobject_type & Hitobject.SLIDER > 0:
                beatmap.hitobjects.append(StdHoldNoteHitobjectBase(
                    posx    = int(data[0]), 
                    posy    = int(data[1]), 
                    tstart  = int(data[2]), 
                    htype   = int(data[3]),
                    sdata   = data[5],
                    repeats = int(data[6]),
                    px_len  = float(data[7]),
                ))
                return

            if hitobject_type & Hitobject.SPINNER > 0:
                beatmap.hitobjects.append(StdSpinnerHitobjectBase(
                    posx   = int(data[0]),
                    posy   = int(data[1]),
                    tstart = int(data[2]),
                    htype  = int(data[3]),
                    tend   = int(data[5]),
                ))
                return

            raise BeatmapIO.BeatmapIOException(f'Unexpected osu!std hitobject encountered: {hitobject_type}')
            
        if beatmap.gamemode == Gamemode(Gamemode.TAIKO):
            raise BeatmapIO.BeatmapIOException('No support osu!taiko gamemode yet!')

            if hitobject_type & Hitobject.CIRCLE > 0:
                #beatmap.hitobjects.append(TaikoSingleNoteHitobject(data))
                return

            if hitobject_type & Hitobject.SLIDER > 0:
                #beatmap.hitobjects.append(TaikoHoldNoteHitobject(data))
                return

            if hitobject_type & Hitobject.SPINNER > 0:
                #beatmap.hitobjects.append(TaikoSpinnerHitobject(data))
                return

            raise BeatmapIO.BeatmapIOException(f'Unexpected osu!taiko hitobject encountered: {hitobject_type}')

        if beatmap.gamemode == Gamemode(Gamemode.CATCH):
            raise BeatmapIO.BeatmapIOException('No support osu!catch gamemode yet!')

            if hitobject_type & Hitobject.CIRCLE > 0:
                #beatmap.hitobjects.append(CatchSingleNoteHitobject(data))
                return

            if hitobject_type & Hitobject.SLIDER > 0:
                #beatmap.hitobjects.append(CatchHoldNoteHitobject(data))
                return

            if hitobject_type & Hitobject.SPINNER > 0:
                #beatmap.hitobjects.append(CatchSpinnerHitobject(data))
                return

            raise BeatmapIO.BeatmapIOException(f'Unexpected osu!catch hitobject encountered: {hitobject_type}')

        if beatmap.gamemode == Gamemode(Gamemode.MANIA):
            if hitobject_type & Hitobject.CIRCLE > 0:
                beatmap.hitobjects.append(ManiaSingleNoteHitobjectBase(
                    posx   = int(data[0]),
                    posy   = int(data[1]),
                    tstart = int(data[2]), 
                    htype  = int(data[3]),
                    keys   = beatmap.difficulty.cs
                ))
                return

            if hitobject_type & Hitobject.MANIALONG > 0:
                beatmap.hitobjects.append(ManiaHoldNoteHitobjectBase(
                    posx   = int(data[0]),
                    posy   = int(data[1]),
                    tstart = int(data[2]),
                    htype  = int(data[3]),
                    sdata  = data[5],
                    keys   = beatmap.difficulty.cs
                ))
                return

            raise BeatmapIO.BeatmapIOException(f'Unexpected osu!mania hitobject encountered: {hitobject_type}')


    @staticmethod
    def __process_timing_points(beatmap):
        beatmap.bpm_min = float('inf')
        beatmap.bpm_max = float('-inf')

        bpm = 0
        slider_multiplier = -100
        old_beat = -100
        base = 0

        for timing_point in beatmap.timing_points:
            if timing_point.inherited:
                    timing_point.beat_length = base

                    if timing_point.beat_interval < 0:
                        slider_multiplier = timing_point.beat_interval
                        old_beat = timing_point.beat_interval
                    else:
                        slider_multiplier = old_beat
            else:
                slider_multiplier = -100
                bpm = 60000 / timing_point.beat_interval
                timing_point.beat_length = timing_point.beat_interval
                base = timing_point.beat_interval

                beatmap.bpm_min = min(beatmap.bpm_min, bpm)
                beatmap.bpm_max = max(beatmap.bpm_max, bpm)

            timing_point.bpm = bpm
            timing_point.slider_multiplier = slider_multiplier


    @staticmethod
    def __postprocess_hitobjects(beatmap):
        for hitobject in beatmap.hitobjects:
            if beatmap.gamemode == Gamemode.OSU or beatmap.gamemode == None:
                if not hitobject.is_htype(Hitobject.SLIDER):
                    hitobject.generate_tick_data()
                    continue

                # Find the last timing that occurs before the hitobject starts
                for timing_point in beatmap.timing_points:
                    if timing_point.offset > hitobject.start_time():
                        break

                to_repeat_time = round(((-600.0/timing_point.bpm) * hitobject.px_len * timing_point.slider_multiplier) / (100.0 * beatmap.difficulty.sm))
                end_time = hitobject.start_time() + to_repeat_time*hitobject.repeats

                hitobject.generate_tick_data(end_time=end_time, sm=beatmap.difficulty.sm, st=beatmap.difficulty.st)

            else:
                hitobject.generate_tick_data()

BeatmapIO.init()
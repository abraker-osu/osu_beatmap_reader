"""
Opens a beatmap and prints its metadata

NOTE: If changes were made, run refresh.bat to apply beatmap_reader changes to venv
"""
from beatmap_reader import BeatmapIO

if __name__ == '__main__':
    beatmap = BeatmapIO.open_beatmap('test/data/maps/osu/stargazer.osu')

    print(f'Beatmap: {beatmap.metadata.artist} - {beatmap.metadata.title}[{beatmap.metadata.version}] ({beatmap.metadata.creator})')
    print(f'Gamemode: {beatmap.gamemode}')

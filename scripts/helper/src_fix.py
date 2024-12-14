"""
Used to correct pip installing editable directories
bearing dashes instead of underscores
"""
import os


if 'VIRTUAL_ENV' not in os.environ:
    raise Exception('No virtual environment active!')


path = f'{os.environ["VIRTUAL_ENV"]}\\src'
for subdir in os.listdir(path):
    old_path = f'{path}\\{subdir}'

    # Make path relative
    old_path = old_path.replace(f'{os.getcwd()}\\', '')

    if '-' in subdir:
        new_path = old_path.replace('-', '_')

        print(f'Renaming {old_path} to {new_path}')
        os.removedirs(old_path)
        os.rename(old_path, new_path)
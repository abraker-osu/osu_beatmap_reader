@echo off

echo Removing ".eggs/..."
rd /s /q .eggs

echo Removing "build/..."
rd /s /q build

echo Removing "src/osu_beatmap_reader.egg-info"
rd /s /q src\\osu_beatmap_reader.egg-info

call venv\\Scripts\\activate.bat
if %ERRORLEVEL% GEQ 1 (
    echo Failed to activate virtual environment!
    EXIT /B 1
)

if "%VIRTUAL_ENV%" == "" (
    echo Virtual environment not active!
    EXIT /B 1
)

echo uninstall lib...
python -m pip uninstall -y osu_beatmap_reader


echo Removing "pycache..."
python -Bc "import pathlib; import shutil; [ shutil.rmtree(path) for path in pathlib.Path('.').rglob('__pycache__') ]"

python -m pip cache purge

echo [ DONE ]

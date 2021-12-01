# https://cx-freeze.readthedocs.io/en/latest/distutils.html

import sys
from cx_Freeze import setup, Executable

includes = []

# Include your files and folders
includefiles = ['lvl/','res/','Box.py','Camera.py','ComponentFrequencyCritic.py','Critic.py','DifficultyCritic.py','EmptynessCritic.py','Game.py','Lava.py','Level.py','LevelPiece.py','LineCritic.py','Particle.py','Platform.py','Player.py','Song.py','Spike.py','VarietyCritic.py']

# Exclude unnecessary packages
#excludes = ['cx_Freeze','pydoc_data','setuptools','distutils','tkinter']

# Dependencies are automatically detected, but some modules need help.
#packages = ['kivy','kivymd', 'ffpyplayer','gtts']

base = None
shortcutName = None
shortcutDir = None
if sys.platform == "win32":
    base = "Win32GUI"
    shortcutName='My App'
    shortcutDir="DesktopFolder"

setup(
    name = 'MyApp',
    version = '0.1',
    description = 'Sample python app',
    author = 'your name',
    author_email = '',
    options = {'build_exe': {
        'includes': includes,
        'excludes': [],
        'packages': [],
        'include_files': includefiles}
        },
    executables = [Executable('Main.py',
    base = base, # "Console", base, # None
    icon='res/icon.ico',
    shortcutName = shortcutName,
    shortcutDir = shortcutDir)]
)
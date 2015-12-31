from distutils.core	import setup
import py2exe

setup(console=['WinTriage_v1.py'])

setup(
    options={'py2exe': {'bundle_files': 1, 'compressed': True}},
    windows=[{'script': "single.py"}],
    zipfile=None,
)
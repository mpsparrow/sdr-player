import sys
from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="sdr-player",
    version="0.1",
    description="RTL-SDR WFM player",
    author="Matthew Sparrow",
    url="https://github.com/mpsparrow/sdr-rec",
    executables=[Executable("./sdr-player/listen.py", base=base)],
)

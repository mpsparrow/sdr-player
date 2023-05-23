import sys
from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="sdr-player",
    version="0.2-alpha",
    description="RTL-SDR WFM Player",
    author="Matthew Sparrow",
    url="https://github.com/mpsparrow/sdr-rec",
    executables=[Executable("./sdr-player/main.py", base=base)],
)

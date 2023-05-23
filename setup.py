import sys
from cx_Freeze import setup, Executable

includefiles = ["README.md", "LICENSE"]
packages = [
    "numpy",
    "pyaudio",
    "rtlsdr",
    "ttkthemes",
    "tkinter",
    "threading",
    "sys",
    "sdr_player",
]

setup(
    name="sdr-player",
    version="0.2-alpha",
    description="RTL-SDR WFM Player",
    author="Matthew Sparrow",
    url="https://github.com/mpsparrow/sdr-rec",
    options={
        "build_exe": {
            "include_files": includefiles,
            "packages": packages,
        }
    },
    executables=[
        Executable("main.py", base="Win32GUI", targetName="sdr-player.exe"),
    ],
)

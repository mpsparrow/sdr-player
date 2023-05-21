from distutils.core import setup

setup(
    name="sdr-rec",
    version="1.0",
    description="RTL-SDR audio recorder",
    author="Matthew Sparrow",
    url="https://github.com/mpsparrow/sdr-rec",
    packages=["distutils", "distutils.command", pyrtlsdr],
)

# tests for displaying a spectrum

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from rtlsdr import RtlSdr

sdr = RtlSdr()

# configure device
sdr.sample_rate = 1.024e6
sdr.center_freq = 100.3e6
sdr.gain = 19.7

fig, ax = plt.subplots()


def update_graph(frame):
    samples = sdr.read_samples(1024)  # Reduce the number of samples
    ax.clear()
    ax.psd(
        samples, NFFT=512, Fs=sdr.sample_rate / 1e6, Fc=sdr.center_freq / 1e6
    )  # Adjust the NFFT parameter
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Relative power (dB)")
    ax.set_ylim(-40, 10)  # Set the y-axis limits


ani = animation.FuncAnimation(fig, update_graph, interval=50)

plt.show()

sdr.close()

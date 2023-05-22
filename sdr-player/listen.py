import numpy as np
import pyaudio
from rtlsdr import RtlSdr
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from threading import Thread, Event


class RadioStationRecorder:
    def __init__(self):
        self.stop_flag = Event()
        self.audio_thread = None

        # Create the main window
        self.window = ThemedTk(theme="yaru")
        self.window.title("WFM Radio Player")
        self.window.geometry("400x200")

        # Create style for the UI elements
        style = ttk.Style(self.window)
        style.configure("TEntry", padding=5, relief="solid")

        # Create menu
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        # Create file menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Quit", command=self.window.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Create help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Help", command=self.open_help_window)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # Create a frame to hold the UI elements
        self.frame = ttk.Frame(self.window)
        self.frame.pack(padx=10, pady=10)

        # Create labels and entry fields for frequency
        self.frequency_label = ttk.Label(self.frame, text="Frequency (MHz):")
        self.frequency_label.grid(row=0, column=0, sticky=tk.W)
        self.frequency_entry = ttk.Entry(self.frame)
        self.frequency_entry.grid(row=0, column=1, sticky=tk.W)
        self.frequency_entry.insert(0, "100.3")  # Default frequency

        # Create label and entry field for PPM correction
        self.ppm_label = ttk.Label(self.frame, text="PPM Correction:")
        self.ppm_label.grid(row=1, column=0, sticky=tk.W)
        self.ppm_entry = ttk.Entry(self.frame)
        self.ppm_entry.grid(row=1, column=1, sticky=tk.W)
        self.ppm_entry.insert(0, "1")  # Set default value to 1

        # Create label and slider for gain
        self.gain_label = ttk.Label(self.frame, text="Gain (dB):")
        self.gain_label.grid(row=2, column=0, sticky=tk.W)
        self.gain_slider = ttk.Scale(
            self.frame, from_=0, to=49.6, length=200, orient=tk.HORIZONTAL
        )
        self.gain_slider.grid(row=2, column=1, sticky=tk.W)
        self.gain_slider.set(19.7)  # Default gain

        # Create label and slider for volume
        self.volume_label = ttk.Label(self.frame, text="Volume:")
        self.volume_label.grid(row=3, column=0, sticky=tk.W)
        self.volume_slider = ttk.Scale(
            self.frame, from_=0, to=100, length=200, orient=tk.HORIZONTAL
        )
        self.volume_slider.grid(row=3, column=1, sticky=tk.W)
        self.volume_slider.set(100)  # Default volume

        # Create a frame to hold the buttons
        self.button_frame = ttk.Frame(self.window)
        self.button_frame.pack(padx=10, pady=10)

        # Create buttons for play and stop
        self.play_button = ttk.Button(
            self.button_frame, text="Play", command=self.start_audio
        )
        self.play_button.grid(row=0, column=0, padx=5)
        self.pause_button = ttk.Button(
            self.button_frame, text="Pause", command=self.stop_audio, state=tk.DISABLED
        )
        self.pause_button.grid(row=0, column=1, padx=5)

    def start_audio(self):
        if self.audio_thread is None or not self.audio_thread.is_alive():
            # Clear the stop flag and start audio playback
            self.stop_flag.clear()

            self.set_ui_state(False)  # Disable UI controls during audio playback

            audio_chunks = self.record_radio_station()
            sample_rate = 250e3

            volume = self.volume_slider.get() / 100  # Adjust volume range to 0.0-1.0
            self.audio_thread = Thread(
                target=self.play_audio_chunks, args=(audio_chunks, sample_rate, volume)
            )
            self.audio_thread.daemon = True
            self.audio_thread.start()

    def stop_audio(self):
        # Set the stop flag to stop audio playback
        self.stop_flag.set()

        self.set_ui_state(True)  # Enable UI controls after stopping audio playback

    def get_frequency(self):
        frequency_entry_value = self.frequency_entry.get()
        frequency = (
            float(frequency_entry_value) * 1e6 if frequency_entry_value else 100.3e6
        )
        return frequency

    def get_ppm(self):
        ppm_entry_value = self.ppm_entry.get()
        ppm = (
            int(ppm_entry_value) if ppm_entry_value else 1
        )  # Updated default value to 1
        return ppm

    def record_radio_station(self):
        # Configure RTL-SDR device
        sdr = RtlSdr()
        sdr.sample_rate = 250e3
        sdr.center_freq = int(self.get_frequency())
        sdr.gain = self.gain_slider.get()
        sdr.set_freq_correction(self.get_ppm())

        # Create a generator function to yield audio chunks
        def generate_audio_chunks():
            while not self.stop_flag.is_set():
                samples = sdr.read_samples(1024)
                audio = np.angle(samples[1:] * np.conj(samples[:-1]))
                audio /= np.max(np.abs(audio))
                yield audio

        return generate_audio_chunks()

    def play_audio_chunks(self, audio_chunks, sample_rate, volume):
        p = pyaudio.PyAudio()

        stream = p.open(
            format=pyaudio.paFloat32, channels=1, rate=int(sample_rate), output=True
        )

        for chunk in audio_chunks:
            if self.stop_flag.is_set():
                break
            chunk *= volume  # Apply volume adjustment
            stream.write(chunk.astype(np.float32).tobytes())

        stream.stop_stream()
        stream.close()

        p.terminate()

        self.set_ui_state(True)  # Enable UI controls after audio playback finishes

    def set_ui_state(self, enabled):
        self.frequency_entry["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.ppm_entry["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.gain_slider["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.volume_slider["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.play_button["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.pause_button["state"] = tk.DISABLED if enabled else tk.NORMAL

    def open_help_window(self):
        # Open a help window with a link to the GitHub project
        help_window = tk.Toplevel(self.window)
        help_window.title("Help")
        help_window.geometry("250x50")

        help_label = ttk.Label(help_window, text="For more information, visit:")
        help_label.pack()

        github_link = ttk.Label(
            help_window,
            text="https://github.com/mpsparrow/sdr-player",
            foreground="blue",
            cursor="hand2",
        )
        github_link.pack()
        github_link.bind(
            "<Button-1>",
            lambda e: self.open_github_project(
                "https://github.com/mpsparrow/sdr-player"
            ),
        )

    def open_github_project(self, url):
        import webbrowser

        webbrowser.open_new(url)

    def run(self):
        # Start the main event loop
        self.window.mainloop()


if __name__ == "__main__":
    recorder = RadioStationRecorder()
    recorder.run()

import numpy as np
import pyaudio
from rtlsdr import RtlSdr
from threading import Thread, Event
from gui import GUI


class RadioStationRecorder:
    def __init__(self):
        self.stop_flag = Event()
        self.audio_thread = None
        self.gui = GUI(self)

    def start_audio(self):
        if self.audio_thread is None or not self.audio_thread.is_alive():
            # Clear the stop flag and start audio playback
            self.stop_flag.clear()

            self.gui.set_ui_state(False)  # Disable UI controls during audio playback

            audio_chunks = self.record_radio_station()
            sample_rate = 250e3

            volume = (
                self.gui.volume_slider.get() / 100
            )  # Adjust volume range to 0.0-1.0
            audio_mode = self.gui.audio_mode_var.get()
            if audio_mode == "True":
                stereo = True
            else:
                stereo = False
            self.audio_thread = Thread(
                target=self.play_audio_chunks,
                args=(audio_chunks, sample_rate, volume),
                kwargs={"stereo": stereo},  # Always use stereo mode
            )
            self.audio_thread.daemon = True
            self.audio_thread.start()

    def stop_audio(self):
        # Set the stop flag to stop audio playback
        self.stop_flag.set()

        self.gui.set_ui_state(True)  # Enable UI controls after stopping audio playback

    def get_frequency(self):
        frequency_entry_value = self.gui.frequency_entry.get()
        frequency = (
            float(frequency_entry_value) * 1e6 if frequency_entry_value else 100.3e6
        )
        return frequency

    def get_ppm(self):
        ppm_entry_value = self.gui.ppm_entry.get()
        ppm = (
            int(ppm_entry_value) if ppm_entry_value else 1
        )  # Updated default value to 1
        return ppm

    def record_radio_station(self):
        # Configure RTL-SDR device
        sdr = RtlSdr()
        sdr.sample_rate = 250e3
        sdr.center_freq = int(self.get_frequency())
        sdr.gain = self.gui.gain_slider.get()
        sdr.set_freq_correction(self.get_ppm())

        # Create a generator function to yield audio chunks
        def generate_audio_chunks():
            while not self.stop_flag.is_set():
                samples = sdr.read_samples(1024)
                audio = np.angle(samples[1:] * np.conj(samples[:-1]))
                audio /= np.max(np.abs(audio))
                yield audio

        return generate_audio_chunks()

    def play_audio_chunks(self, audio_chunks, sample_rate, volume, stereo):
        p = pyaudio.PyAudio()

        if stereo:
            print(
                f"F: {int(self.get_frequency())}",
                f"SR: {sample_rate}",
                "AM: S",
                f"V: {round(self.gui.volume_slider.get(),2)}",
                f"G: {round(self.gui.gain_slider.get(), 1)}",
            )
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=2,
                rate=int(sample_rate),
                output=True,
            )

            for chunk in audio_chunks:
                if self.stop_flag.is_set():
                    break

                # Generate different audio for left and right channels
                phase_shift = np.pi / 4  # Phase shift between channels (45 degrees)
                chunk_left = chunk * np.cos(phase_shift)
                chunk_right = chunk * np.sin(phase_shift)

                # Apply volume adjustment
                chunk_left *= volume
                chunk_right *= volume

                # Combine left and right channels
                chunk_stereo = np.column_stack((chunk_left, chunk_right))
                stream.write(chunk_stereo.astype(np.float32).tobytes())
        else:
            print(
                f"F: {int(self.get_frequency())}",
                f"SR: {sample_rate}",
                "AM: M",
                f"V: {round(self.gui.volume_slider.get(),2)}",
                f"G: {round(self.gui.gain_slider.get(), 1)}",
            )
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

        self.gui.set_ui_state(True)  # Enable UI controls after audio playback finishes

    def run(self):
        self.gui.run()


if __name__ == "__main__":
    recorder = RadioStationRecorder()
    gui = GUI(recorder)
    recorder.gui = gui
    gui.run()

import sys
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk


class GUI:
    def __init__(self, recorder):
        self.recorder = recorder
        self.window = ThemedTk(theme="yaru")
        self.window.title("RTL-SDR WFM Player")
        self.window.geometry("450x380")
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Quit", command=self.window.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Help", command=self.open_help_window)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.frame = ttk.Frame(self.window)
        self.frame.pack(padx=10, pady=10)
        self.frequency_label = ttk.Label(self.frame, text="Frequency (MHz):")
        self.frequency_label.grid(row=0, column=0, sticky=tk.W)
        self.frequency_entry = ttk.Entry(self.frame)
        self.frequency_entry.grid(row=0, column=1, sticky=tk.W)
        self.frequency_entry.insert(0, "100.3")  # Default frequency
        self.ppm_label = ttk.Label(self.frame, text="PPM Correction:")
        self.ppm_label.grid(row=1, column=0, sticky=tk.W)
        self.ppm_entry = ttk.Entry(self.frame)
        self.ppm_entry.grid(row=1, column=1, sticky=tk.W)
        self.ppm_entry.insert(0, "1")  # Set default value to 1
        self.gain_label = ttk.Label(self.frame, text="Gain (dB):")
        self.gain_label.grid(row=2, column=0, sticky=tk.W)
        self.gain_slider = ttk.Scale(
            self.frame, from_=0, to=49.6, length=200, orient=tk.HORIZONTAL
        )
        self.gain_slider.grid(row=2, column=1, sticky=tk.W)
        self.gain_slider.set(19.7)  # Default gain
        self.volume_label = ttk.Label(self.frame, text="Volume:")
        self.volume_label.grid(row=3, column=0, sticky=tk.W)
        self.volume_slider = ttk.Scale(
            self.frame, from_=0, to=100, length=200, orient=tk.HORIZONTAL
        )
        self.volume_slider.grid(row=3, column=1, sticky=tk.W)
        self.volume_slider.set(50)  # Default volume
        self.audio_mode_label = ttk.Label(self.frame, text="Audio Mode:")
        self.audio_mode_label.grid(row=4, column=0, sticky=tk.W)
        self.audio_mode_var = tk.StringVar(value="True")
        self.stereo_radio = ttk.Radiobutton(
            self.frame,
            text="Stereo",
            variable=self.audio_mode_var,
            value="True",
        )
        self.stereo_radio.grid(row=4, column=1, sticky=tk.W)
        self.mono_radio = ttk.Radiobutton(
            self.frame,
            text="Mono",
            variable=self.audio_mode_var,
            value="False",
        )
        self.mono_radio.grid(row=5, column=1, sticky=tk.W)
        self.button_frame = ttk.Frame(self.window)
        self.button_frame.pack(padx=10, pady=10)
        self.play_button = ttk.Button(
            self.button_frame, text="Play", command=self.recorder.start_audio
        )
        self.play_button.grid(row=0, column=0, padx=5)
        self.pause_button = ttk.Button(
            self.button_frame,
            text="Pause",
            command=self.recorder.stop_audio,
            state=tk.DISABLED,
        )
        self.pause_button.grid(row=0, column=1, padx=5)
        self.log_frame = ttk.Frame(self.window)
        self.log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.log_scrollbar = tk.Scrollbar(self.log_frame)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(
            self.log_frame,
            height=10,
            state=tk.DISABLED,
            yscrollcommand=self.log_scrollbar.set,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_scrollbar.config(command=self.log_text.yview)
        self.redirect_console_output()

    def redirect_console_output(self):
        class ConsoleRedirect:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, message):
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)

            def flush(self):
                pass

        sys.stdout = ConsoleRedirect(self.log_text)

    def set_ui_state(self, enabled):
        self.frequency_entry["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.ppm_entry["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.gain_slider["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.volume_slider["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.stereo_radio["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.mono_radio["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.play_button["state"] = tk.NORMAL if enabled else tk.DISABLED
        self.pause_button["state"] = tk.DISABLED if enabled else tk.NORMAL

    def open_help_window(self):
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
        self.window.mainloop()

'''
    Required Packages: numpy, pandas, scipy, tkinter, pyaudio, matplotlib
'''
import math
import random
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy import signal
from scipy.io import wavfile
import tkinter as tk
from tkinter import ttk
import pyaudio
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sounddevice as sd
import mydsplib as mdl

# GLOBAL PARAMETERS
LARGE_FONT = ("Verdana", 12)
# sample params
SAMPLE_RATE = 44100
DURATION = 2.0
NUM_SAMPLES_TO_PLOT = 1000
# filter params
FILTER_ORDER = 3
CUTOFF = 1000
BAND = [440, 880]
WINDOW_SIZE = 51
# fft params
FFT_MAX_FREQ = 2000

class MultiFrequencyPlayer(tk.Tk):

    def __init__(self, *args, **kwargs):
        # Make a basic tkinter page
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Multi Frequency Player")
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")

        self.frames = {}
        frame = StartPage(container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        # Initialize Plots
        self.f, (self.a, self.fft) = plt.subplots(2, 1, figsize=(5, 6))
        self.f.tight_layout(pad=4.0)

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Multi Frequency Player!", font=LARGE_FONT)

        # Amplitude Slider
        self.text_a = tk.Label(self, font=LARGE_FONT, text='Amplitudes!')
        self.amplitude_sliders = []
        for i in range(13):
            self.amplitude_sliders.append(tk.Scale(self, orient=tk.VERTICAL, from_=1, to=0, digits=3, resolution=0.01, showvalue=False, command=lambda a, index=i: self.update_ampl(a, index)))
            self.amplitude_sliders[i].set(0.0)
        # Initialize to A minor chord because I want to die
        self.amplitude_sliders[0].set(1.0)
        self.amplitude_sliders[3].set(1.0)
        self.amplitude_sliders[7].set(1.0)
        self.amplitude_sliders[12].set(1.0)
        self.note_labels = []
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='A'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='A#'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='B'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='C'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='C#'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='D'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='D#'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='E'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='F'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='F#'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='G'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='G#'))
        self.note_labels.append(tk.Label(self, font=LARGE_FONT, text='A'))

        # Noise Type Buttons
        self.text_ntype = tk.Label(self, font=LARGE_FONT, text=('Noise type is none'))
        self.noise_n_btn = tk.Button(self, text="NONE", command=lambda:self.update_noise_type("none"))
        self.noise_w_btn = tk.Button(self, text="WHITE", command=lambda:self.update_noise_type("white"))
        self.noise_p_btn = tk.Button(self, text="PINK", command=lambda:self.update_noise_type("pink"))

        # Noise Amplitude Slider
        self.text_n = tk.Label(self, font=LARGE_FONT)
        noise_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                         from_=0, to=1, digits=3,
                         resolution=0.01, showvalue=False,
                         command=self.update_noise_ampl)
        noise_slider.set(0.5)

        # Volume
        text_volume = tk.Label(self, font=LARGE_FONT, text="Volume")
        volume_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                         from_=0, to=1, digits=3,
                         resolution=0.01, showvalue=False,
                         command=self.update_volume)
        volume_slider.set(0.5)

        # Random button
        random_button = tk.Button(self, text='DO NOT CLICK ME', command=self.update_random)

        # Filter buttons
        self.text_ftype = tk.Label(self, font=LARGE_FONT, text=('Filter type is none'))
        self.text_low_cutoff = tk.Text(self, height=1, width=6)
        self.text_high_cutoff = tk.Text(self, height=1, width=6)
        self.button_update_cutoff = tk.Button(self, text="UPDATE CUTOFF", command=self.update_filter_cutoff)
        self.filter_n_btn = tk.Button(self, text="NONE",
                                     command=lambda:self.update_filter_type("none"))
        self.filter_l_btn = tk.Button(self, text="LOWPASS",
                                     command=lambda:self.update_filter_type("lowpass"))
        self.filter_h_btn = tk.Button(self, text="HIGHPASS",
                                     command=lambda:self.update_filter_type("highpass"))
        self.filter_b_btn = tk.Button(self, text="BANDPASS",
                                     command=lambda:self.update_filter_type("bandpass"))
        self.filter_s_btn = tk.Button(self, text="SMOOTHING",
                                     command=lambda:self.update_filter_type("smoothing"))

        # Some internal states
        self.sample = np.zeros((200, 1))
        self.noise_type = 'none'
        self.noise_ampl = 0.5
        self.filter_type = 'none'
        self.ampl = []
        self.freq = []
        for i in range(13):
            self.ampl.append(self.amplitude_sliders[i].get())
            self.freq.append(440.0 * math.pow(2, i/12))
        self.volume = 0.8
        self.cutoff = CUTOFF
        self.band = BAND
        self.filter_order = FILTER_ORDER
        self.window_size = WINDOW_SIZE
        self.sample_rate = SAMPLE_RATE # Hz
        self.duration = DURATION # second

        # OTHER STUFF
        self.n = np.arange(self.sample_rate * self.duration)
        self.time_axis = self.n / self.sample_rate
        # print(self.n)
        # print(self.time_axis)

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()

        # GRIDS
        label.grid(row=0, column=0, columnspan=14)
        self.text_a.grid(row=1, column=0, columnspan=14)
        for i in range(13):
            self.amplitude_sliders[i].grid(row=2, column=i, columnspan=1)
            self.note_labels[i].grid(row=3, column=i, columnspan=1)

        self.text_ntype.grid(row=4, column=0, columnspan=6)
        self.noise_n_btn.grid(row=5, column=0, columnspan=2)
        self.noise_w_btn.grid(row=5, column=2, columnspan=2)
        self.noise_p_btn.grid(row=5, column=4, columnspan=2)

        self.text_n.grid(row=4, column=6, columnspan=3)
        noise_slider.grid(row=4, column=9, columnspan=4)
        text_volume.grid(row=5, column=6, columnspan=3)
        volume_slider.grid(row=5, column=9, columnspan=4)

        self.text_ftype.grid(row=6, column=0, columnspan=5)
        self.text_low_cutoff.grid(row=6, column=5, columnspan=2)
        self.text_high_cutoff.grid(row=6, column=7, columnspan=2)
        self.button_update_cutoff.grid(row=6, column=9, columnspan=3)

        self.filter_n_btn.grid(row=7, column=0, columnspan=4)
        self.filter_l_btn.grid(row=7, column=4, columnspan=4)
        self.filter_h_btn.grid(row=7, column=8, columnspan=4)
        self.filter_b_btn.grid(row=8, column=2, columnspan=4)
        self.filter_s_btn.grid(row=8, column=6, columnspan=4)
        random_button.grid(row=9, column=0, columnspan=13)
        self.canvas.get_tk_widget().grid(row=10, column=0, columnspan=13)
        self.canvas._tkcanvas.grid(row=11, column=0, columnspan=13)

    def update_noise_type(self, t):
        self.noise_type = t
        self.text_ntype.configure(text='Noise type is '+t)
        self.update_graph_handler()

    def update_noise_ampl(self, a):
        self.noise_ampl = float(a)
        self.text_n.configure(text=('amp = ' + str(self.noise_ampl)))
        self.update_graph_handler()

    def update_filter_type(self, t):
        self.filter_type=t
        self.text_ftype.configure(text='Filter type is '+t)
        self.update_graph_handler()

    def update_filter_cutoff(self):
        try:
            l = int(self.text_low_cutoff.get("1.0", tk.END).strip())
            h = int(self.text_high_cutoff.get("1.0", tk.END).strip())
        except:
            print("UPDATE FREQUENCY FAILED\nPLEASE CHECK FREQUENCY")
            print("\t0 <= low < high <= 2000\n")
            return

        if l >= h or l < 0 or h > 2000:
            print("UPDATE FREQUENCY FAILED, PLEASE CHECK FREQUENCY")
            print("\t0 <= low < high <= 2000\n")
            return

        self.band = [l, h]
        self.update_graph_handler()

    def update_volume(self, v):
        self.volume = v

    def update_ampl(self, a, i):
        # update amplitudes
        self.ampl[i] = float(a)
        self.update_graph_handler()

    def update_graph_handler(self):
        # update sample
        self.sample = np.zeros(int(self.sample_rate*self.duration)).astype(np.float32)
        for i in range(13):
            self.sample += self.ampl[i] * np.sin(2 * np.pi * self.freq[i] * self.time_axis).astype(np.float32)
        if any(a > 0.0 for a in self.ampl):
            self.sample /= self.sample.max() # normalize
        self.sample = mdl.add_noise(self.sample, self.noise_type, self.noise_ampl, self.sample_rate, self.duration)
        self.sample = mdl.add_filter(self.sample, self.filter_type, self.cutoff, self.band, self.filter_order, self.window_size, self.sample_rate)
        self.sample = mdl.normalize_sample(self.sample)
        # mdl.save_to_wav(self.smaple, 'multi.wav', self.sample_rate)
        self.update_graph()

    def update_graph(self):
        # TODO: Make these plots look better
        # print(self.ampl * self.sample[:10])
        self.a.clear()
        self.a.plot(self.time_axis[:NUM_SAMPLES_TO_PLOT], self.sample[:NUM_SAMPLES_TO_PLOT])
        self.a.set_title('Time Domain Plot')
        self.a.set_xlabel('Time (s)')
        self.a.set_ylabel('Amplitude')

        self.fft.clear()
        self.fft.set_title('Frequency Domain Plot')

        if any(s > 0.0 for s in self.sample):
            # https://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
            # truncate the FFT
            yf = fftpack.fft(self.sample[:self.sample_rate])
            d = len(yf) // 2
            yf = yf[:d-1]
            yp = np.abs(yf) ** 2
            fft_freq = fftpack.fftfreq(len(yp), 1/len(yp))
            i = (fft_freq[:FFT_MAX_FREQ]>0)
            fft_freq = fft_freq[:FFT_MAX_FREQ]
            yp = yp[:FFT_MAX_FREQ]
            self.fft.plot(fft_freq[i], 10*np.log10(yp[i]))
            self.fft.set_xlabel('Frequency (Hz)')
            self.fft.set_ylabel('PSD (dB)')

        self.canvas.draw()
        sd.play(self.sample, self.sample_rate)

    def update_random(self):
        for i in range(13):
            self.amplitude_sliders[i].set(random.random())

if __name__ == "__main__":
    app = MultiFrequencyPlayer()

    def on_closing():
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

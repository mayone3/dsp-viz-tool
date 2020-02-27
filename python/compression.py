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
FILENAME = 'marching_illini.wav'
# sample params
NUM_SAMPLES_TO_PLOT = 1000
# fft params
FFT_MAX_FREQ = 3000

class AudioCompressor(tk.Tk):

    def __init__(self, *args, **kwargs):
        # Make a basic tkinter page
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Audio Compressor")
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
        self.figure, ((self.data, self.carrier), (self.am, self.am_fft)) = plt.subplots(2, 2, figsize=(16, 6))
        self.figure.tight_layout(pad=4.0)

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Audio Compressor!", font=LARGE_FONT)

        # Some internal states
        self.sample_rate, self.sample_orig = wavfile.read(FILENAME)
        self.sample_orig = np.array(self.sample_orig).astype(np.float32)
        self.sample_orig /= self.sample_orig.max()
        self.sample_comp = np.zeros(len(self.sample_orig))
        self.q = 3

        # GUI on the left
        self.text_audiofile_title = tk.Label(self, font=LARGE_FONT, text='Audio File')
        self.text_audiofile_name = tk.Label(self, font=LARGE_FONT, text=FILENAME)
        self.text_samplerate_title = tk.Label(self, font=LARGE_FONT, text='Sound format rate (samples/sec)')
        self.text_samplerate_value = tk.Label(self, font=LARGE_FONT, text=str(self.sample_rate))
        self.text_orig_ss_title = tk.Label(self, font=LARGE_FONT, text='Original # of sound samples')
        self.text_orig_ss_value = tk.Label(self, font=LARGE_FONT, text='4096')
        self.text_comp_ss_title = tk.Label(self, font=LARGE_FONT, text='Number of tones')
        self.text_comp_ss_value = tk.Label(self, font=LARGE_FONT)

        tone_slider = tk.Scale(self, orient=tk.HORIZONTAL, from_=1, to=14, showvalue=False, command=self.update_quality)
        tone_slider.set(3)

        # OTHER STUFF
        self.n = np.arange(len(self.sample_orig))
        self.time_axis = self.n / self.sample_rate

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()

        # GRIDS
        label.grid(row=0, column=0, columnspan=6)
        self.text_audiofile_title.grid(row=1, column=0, columnspan=3)
        self.text_audiofile_name.grid(row=2, column=0, columnspan=3)
        self.text_samplerate_title.grid(row=3, column=0, columnspan=3)
        self.text_samplerate_value.grid(row=4, column=0, columnspan=3)
        self.text_orig_ss_title.grid(row=5, column=0, columnspan=3)
        self.text_orig_ss_value.grid(row=6, column=0, columnspan=3)
        tone_slider.grid(row=7, column=0, columnspan=3)
        self.text_comp_ss_title.grid(row=8, column=0, columnspan=3)
        self.text_comp_ss_value.grid(row=9, column=0, columnspan=3)

    def update_quality(self, q):
        q = int(q)
        if q > 10:
            q = 10 * 2**(q-10)
        self.q = q
        self.text_comp_ss_value.configure(text=str(q))
        self.update_audio()

    def update_audio(self):
        self.sample_comp = mdl.compress(self.sample_orig, self.q, self.sample_rate, self.time_axis)
        sd.play(self.sample_comp)

    def update_graph(self):
        if any(self.sample) != 0:
            # https://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
            # truncate the FFT
            yf = fftpack.fft(self.samples[2][:self.sample_rate])
            d = len(yf) // 2
            yf = yf[:d-1]
            yp = np.abs(yf) ** 2
            fft_freq = fftpack.fftfreq(len(yp), 1/len(yp))
            i = (fft_freq[:FFT_MAX_FREQ]>0)
            fft_freq = fft_freq[:FFT_MAX_FREQ]
            yp = yp[:FFT_MAX_FREQ]
            self.am_fft.plot(fft_freq[i], 10*np.log10(yp[i]))

if __name__ == "__main__":
    app = AudioCompressor()

    def on_closing():
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

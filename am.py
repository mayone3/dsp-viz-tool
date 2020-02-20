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
# fft params
FFT_MAX_FREQ = 3000

class AmplitudeModulationPlayer(tk.Tk):

    def __init__(self, *args, **kwargs):
        # Make a basic tkinter page
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "AM Player")
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
        label = tk.Label(self, text="Amplitude Modulation!", font=LARGE_FONT)

        # Frequency Sliders
        self.text_df = tk.Label(self, font=LARGE_FONT, text='Data Frequency')
        self.text_cf = tk.Label(self, font=LARGE_FONT, text='Carrier Frequency')
        frequency_sliders = []
        frequency_sliders.append(tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=400, digits=3, resolution=20, showvalue=True, command=lambda f: self.update_freq(f, 0)))
        frequency_sliders.append(tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=2000, digits=3, resolution=100, showvalue=True, command=lambda f: self.update_freq(f, 1)))
        frequency_sliders[0].set(200)
        frequency_sliders[1].set(1000)

        # Amplitude Sliders
        self.text_da = tk.Label(self, font=LARGE_FONT, text='Data Amplitude')
        self.text_ca = tk.Label(self, font=LARGE_FONT, text='Carrier Amplitude')
        amplitude_sliders = []
        amplitude_sliders.append(tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=1, digits=2, resolution=0.1, showvalue=True, command=lambda a: self.update_ampl(a, 0)))
        amplitude_sliders.append(tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=1, digits=2, resolution=0.1, showvalue=True, command=lambda a: self.update_ampl(a, 1)))
        amplitude_sliders[0].set(0.5)
        amplitude_sliders[1].set(0.5)

        # Some internal states
        self.samples = [np.zeros((200, 1)), np.zeros((200, 1)), np.zeros((200, 1))]
        self.a = [amplitude_sliders[0].get(), amplitude_sliders[1].get()]
        self.f = [frequency_sliders[0].get(), frequency_sliders[1].get()]
        self.sample_rate = SAMPLE_RATE # Hz
        self.duration = DURATION # 1 Second

        # OTHER STUFF
        self.n = np.arange(self.sample_rate * self.duration)
        self.time_axis = self.n / self.sample_rate

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()

        # GRIDS
        label.grid(row=0, column=0, columnspan=2)
        self.text_df.grid(row=1, column=0, columnspan=1)
        frequency_sliders[0].grid(row=2, column=0, columnspan=1)
        self.text_da.grid(row=3, column=0, columnspan=1)
        amplitude_sliders[0].grid(row=4, column=0, columnspan=1)
        self.text_cf.grid(row=1, column=1, columnspan=1)
        frequency_sliders[1].grid(row=2, column=1, columnspan=1)
        self.text_ca.grid(row=3, column=1, columnspan=1)
        amplitude_sliders[1].grid(row=4, column=1, columnspan=1)

        self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2)
        self.canvas._tkcanvas.grid(row=6, column=0, columnspan=2)

    def update_freq(self, f, index):
        self.f[index] = float(f)
        self.update_graph_handler()

    def update_ampl(self, a, index):
        self.a[index] = float(a)
        self.update_graph_handler()

    def update_graph_handler(self):
        # update samples
        self.samples[0] = self.a[0] * np.sin(2*np.pi*self.f[0]*self.time_axis).astype(np.float32)
        self.samples[1] = self.a[1] * np.sin(2*np.pi*self.f[1]*self.time_axis).astype(np.float32)
        self.samples[2] = mdl.am(self.samples[0], self.samples[1], self.a[1])
        if self.samples[2].max() > 1.0:
            self.samples[2] = mdl.normalize_sample(self.samples[2])
        self.update_graph()

    def update_graph(self):
        self.data.clear()
        self.data.plot(self.time_axis[:NUM_SAMPLES_TO_PLOT], self.samples[0][:NUM_SAMPLES_TO_PLOT])
        self.data.set_title('Data Wave in Time Domain')
        self.data.set_xlabel('Time (s)')
        self.data.set_ylabel('Amplitude')

        self.carrier.clear()
        self.carrier.plot(self.time_axis[:NUM_SAMPLES_TO_PLOT], self.samples[1][:NUM_SAMPLES_TO_PLOT])
        self.carrier.set_title('Carrier Wave in Time Domain')
        self.carrier.set_xlabel('Time (s)')
        self.carrier.set_ylabel('Amplitude')

        self.am.clear()
        self.am.plot(self.time_axis[:NUM_SAMPLES_TO_PLOT], self.samples[2][:NUM_SAMPLES_TO_PLOT])
        self.am.set_title('AM Wave in Time Domain')
        self.am.set_xlabel('Time (s)')
        self.am.set_ylabel('Amplitude')

        self.am_fft.clear()
        self.am_fft.set_title('AM Wave in Frequency Domain')
        self.am_fft.set_xlabel('Frequency (Hz)')
        self.am_fft.set_ylabel('PSD (dB)')

        if any(self.samples[2]) != 0:
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

        self.data.set(xlim=(0,0.020), ylim=(-1,1))
        self.carrier.set(xlim=(0,0.020), ylim=(-1,1))
        self.am.set(xlim=(0,0.020), ylim=(-1,1))
        self.canvas.draw()
        sd.play(self.samples[2], self.sample_rate)

if __name__ == "__main__":
    app = AmplitudeModulationPlayer()

    def on_closing():
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

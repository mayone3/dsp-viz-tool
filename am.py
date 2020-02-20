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
# freq params
OCTAVE_SIZE = 4
MIN_FREQ = 440 / math.pow(2, OCTAVE_SIZE/2)
MAX_FREQ = 440 * math.pow(2, OCTAVE_SIZE/2)
DEFAULT_FREQ = math.log(440/MIN_FREQ, 2)
# filter params
FILTER_ORDER = 3
CUTOFF = 1000
BAND = [440, 880]
WINDOW_SIZE = 51
# fft params
FFT_MAX_FREQ = 2000

class FixedFrequencyPlayer(tk.Tk):

    def __init__(self, *args, **kwargs):
        # Make a basic tkinter page
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Fixed Frequency Player")
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
        self.f, (self.a, self.fft) = plt.subplots(2, 2, figsize=(5, 6))
        self.f.tight_layout(pad=4.0)
        self.a.set(xlim=(0,0.010), ylim=(-1,1))

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Fixed Frequency Player!", font=LARGE_FONT)

        # Amplitude Slider
        self.text_a = tk.Label(self, font=LARGE_FONT)
        amplitude_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                             from_=0, to=1, digits=3,
                             resolution=0.01, showvalue=False,
                             command=self.update_ampl)
        amplitude_slider.set(0.5)

        # Frequency Slider
        self.text_f = tk.Label(self, font=LARGE_FONT)
        frequency_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                                 from_=0, to=OCTAVE_SIZE, digit=3,
                                 resolution=1/24, showvalue=False,
                                 command=self.update_freq)
        frequency_slider.set(DEFAULT_FREQ)

        # Noise Dropdown
        # noise_dropdown = tk.StringVar(self)
        # noise_choices = {'None', 'White', 'Pink (power = 1/f)'}
        # noise_dropdown.set('None')
        #
        # noise_menu = tk.OptionMenu(parent, self, *noise_choices)
        # noise_menu.pack()

        # Noise Type Buttons
        self.text_ntype = tk.Label(self, font=LARGE_FONT, text=('Noise type is none'))
        self.noise_n_btn = tk.Button(self, text="NONE",
                                     command=lambda:self.update_noise_type("none"))
        self.noise_w_btn = tk.Button(self, text="WHITE",
                                     command=lambda:self.update_noise_type("white"))
        self.noise_p_btn = tk.Button(self, text="PINK",
                                     command=lambda:self.update_noise_type("pink"))

        # Noise Amplitude Slider
        self.text_n = tk.Label(self, font=LARGE_FONT)
        noise_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                         from_=0, to=1, digits=3,
                         resolution=0.01, showvalue=False,
                         command=self.update_noise_ampl)
        noise_slider.set(0.5)

        # Filter buttons
        self.text_ftype = tk.Label(self, font=LARGE_FONT, text=('Filter type is none'))
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

        # Uncomment this if you want a toolbar at the bottom.
        #toolbar = NavigationToolbar2Tk(self.canvas, self)
        #toolbar.update()

        # Some internal states
        self.sample = np.zeros((200, 1))
        self.noise_type = 'none'
        self.noise_ampl = 0.5
        self.filter_type = 'none'
        self.ampl = amplitude_slider.get()
        self.freq = MIN_FREQ * 2**frequency_slider.get()
        self.cutoff = CUTOFF
        self.band = BAND
        self.filter_order = FILTER_ORDER
        self.window_size = WINDOW_SIZE
        self.sample_rate = SAMPLE_RATE # Hz
        self.duration = DURATION # 1 Second

        # OTHER STUFF
        self.n = np.arange(self.sample_rate * self.duration)
        self.time_axis = self.n / self.sample_rate

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()

        # GRIDS
        label.grid(row=0, column=0, columnspan=4)
        self.text_a.grid(row=1, column=0, columnspan=2)
        amplitude_slider.grid(row=1, column=2, columnspan=2)
        self.text_f.grid(row=2, column=0, columnspan=2)
        frequency_slider.grid(row=2, column=2, columnspan=2)
        self.text_n.grid(row=3, column=0, columnspan=2)
        noise_slider.grid(row=3, column=2, columnspan=2)
        self.text_ntype.grid(row=4, column=0, columnspan=4)
        self.noise_n_btn.grid(row=5, column=0, columnspan=1)
        self.noise_w_btn.grid(row=5, column=1, columnspan=1)
        self.noise_p_btn.grid(row=5, column=2, columnspan=1)
        self.text_ftype.grid(row=6, column=0, columnspan=4)
        self.filter_n_btn.grid(row=7, column=0, columnspan=1)
        self.filter_l_btn.grid(row=7, column=1, columnspan=1)
        self.filter_h_btn.grid(row=7, column=2, columnspan=1)
        self.filter_b_btn.grid(row=8, column=0, columnspan=1)
        self.filter_s_btn.grid(row=8, column=1, columnspan=1)
        self.canvas.get_tk_widget().grid(row=9, column=0, columnspan=4)
        self.canvas._tkcanvas.grid(row=10, column=0, columnspan=4)

        # PACKS
        # label.pack(pady=10,padx=10,expand=True)
        # self.text_a.pack()
        # amplitude_slider.pack()
        # self.text_f.pack()
        # frequency_slider.pack()
        # self.noise_n_btn.pack()
        # self.noise_w_btn.pack()
        # self.noise_p_btn.pack()
        # self.text_n.pack()
        # noise_slider.pack()
        # self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        # self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_noise_type(self, t):
        self.noise_type=t
        self.text_ntype.configure(text='Noise type is '+t)
        self.update_graph_handler()

    def update_noise_ampl(self, a):
        self.noise_ampl = float(a)
        self.text_n.configure(text=('Noise amplitude = ' + str(self.noise_ampl)))
        self.update_graph_handler()

    def update_filter_type(self, t):
        self.filter_type=t
        self.text_ftype.configure(text='Filter type is '+t)
        self.update_graph_handler()

    def update_freq(self, f):
        self.freq = MIN_FREQ * 2**float(f)
        self.text_f.configure(text=('Frequency f = ' + str(round(self.freq, 2))))
        self.update_graph_handler()

    def update_ampl(self, a):
        self.ampl = float(a)
        self.text_a.configure(text=('Amplitude a = ' + str(self.ampl)))
        self.update_graph_handler()

    def update_graph_handler(self):
        # update sample
        self.sample = self.ampl * np.sin(2*np.pi*self.freq*self.time_axis).astype(np.float32)
        self.sample = mdl.add_noise(self.sample, self.noise_type, self.noise_ampl, self.sample_rate, self.duration)
        self.sample = mdl.add_filter(self.sample, self.filter_type, self.cutoff, self.band, self.filter_order, self.window_size, self.sample_rate)
        self.sample = mdl.normalize_sample(self.sample)
        # mdl.save_to_wav(self.smaple, 'fixed.wav', self.sample_rate)
        self.update_graph()

    def update_graph(self):
        self.a.clear()
        self.a.plot(self.time_axis[:NUM_SAMPLES_TO_PLOT], self.sample[:NUM_SAMPLES_TO_PLOT])
        self.a.set_title('Time Domain Plot')
        self.a.set_xlabel('Time (s)')
        self.a.set_ylabel('Amplitude')

        self.fft.clear()
        self.fft.set_title('Frequency Domain Plot')

        if self.ampl != 0:
            # https://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
            # truncate the FFT
            yf = fftpack.fft(self.sample[:self.sample_rate])
            d = len(yf) // 2
            yf = yf[:d-1]
            yp = np.abs(yf) ** 2
            fft_freq = fftpack.fftfreq(len(yp), 1/len(yp))
            i = (fft_freq>0)[:FFT_MAX_FREQ]
            fft_freq = fft_freq[:FFT_MAX_FREQ]
            yp = yp[:FFT_MAX_FREQ]
            self.fft.plot(fft_freq[i], 10*np.log10(yp[i]))
            self.fft.set_xlabel('Frequency (Hz)')
            self.fft.set_ylabel('PSD (dB)')

        self.canvas.draw()
        sd.play(self.sample, self.sample_rate)

if __name__ == "__main__":
    app = FixedFrequencyPlayer()

    def on_closing():
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

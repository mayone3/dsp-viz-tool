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

# GLOBAL PARAMETERS
LARGE_FONT = ("Verdana", 12)
# sample params
SAMPLING_RATE = 44100
DURATION = 2.0
NUM_SAMPLES_TO_PLOT = 1000
# freq params
OCTAVE_SIZE = 4
MIN_FREQ = 440 / math.pow(2, OCTAVE_SIZE/2)
MAX_FREQ = 440 * math.pow(2, OCTAVE_SIZE/2)
DEFAULT_FREQ = math.log(440/MIN_FREQ, 2)
# filter params
FILTER_ORDER = 3
LOWPASS_FREQ = 440
HIGHPASS_FREQ = 880
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
        self.f, (self.a, self.fft) = plt.subplots(2, 1, figsize=(5, 6))
        self.f.tight_layout(pad=4.0)
        self.a.set(xlim=(0,0.010), ylim=(-1,1))

        # TODO: Add filters with the following options
        # lowpass @ 100Hz
        # highpass @ 100Hz
        # bandpass 100-400Hz(IIR 3rd order butterworth)
        # smoothing is MA (moving average) rectangular

        # TODO: Add noise with the following options
        # no noise, white, pink
        # amplitude, filter (smoothing, highpass, lowpass, bandpass)

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Fixed Frequency Player!", font=LARGE_FONT)

        # Amplitude Slider
        self.text_a = tk.Label(self, font=LARGE_FONT)
        amplitude_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                             from_=0, to=1, digits=3,
                             resolution=0.01, showvalue=False,
                             command=self.update_graph_ampl)
        amplitude_slider.set(0.5)

        # Frequency Slider
        self.text_f = tk.Label(self, font=LARGE_FONT)
        frequency_slider = tk.Scale(self, orient=tk.HORIZONTAL,
                                 from_=0, to=OCTAVE_SIZE, digit=3,
                                 resolution=1/24, showvalue=False,
                                 command=self.update_graph_freq)
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
        self.samples = np.zeros((200, 1))
        self.noise_type = 'none'
        self.noise_ampl = 0.5
        self.filter_type = 'none'
        self.ampl = amplitude_slider.get()
        self.freq = MIN_FREQ * 2**frequency_slider.get()
        self.low_cutoff = LOWPASS_FREQ
        self.high_cutoff = HIGHPASS_FREQ
        self.sampling_rate = SAMPLING_RATE # Hz
        self.duration = DURATION # 1 Second

        # OTHER STUFF
        self.n = np.arange(self.sampling_rate * self.duration)
        self.time_axis = self.n / self.sampling_rate

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

    def add_noise(self):
        # Choose noise type
        if self.noise_type == 'white':
            self.samples += self.white_noise()
        elif self.noise_type == 'pink':
            self.samples += self.pink_noise() * 10

    def white_noise(self):
        return self.noise_ampl * (np.random.random(int(self.sampling_rate * self.duration))*2-1).astype(np.float32)

    '''
    source: https://scicomp.stackexchange.com/questions/18987/algorithm-for-high-quality-1-f-noise
    source: https://stackoverflow.com/questions/33933842/how-to-generate-noise-in-frequency-range-with-numpy
    source*: https://www.dsprelated.com/showarticle/908.php
    '''
    def pink_noise(self, nrows=int(SAMPLING_RATE*DURATION), ncols=16):
        """Generates pink noise using the Voss-McCartney algorithm.

        nrows: number of values to generate
        rcols: number of random sources to add

        returns: NumPy array
        """
        array = np.empty([nrows, ncols])
        array.fill(np.nan)
        array[0, :] = np.random.random(ncols)
        array[:, 0] = np.random.random(nrows)

        # the total number of changes is nrows
        n = nrows
        cols = np.random.geometric(0.5, n)
        cols[cols >= ncols] = 0
        rows = np.random.randint(nrows, size=n)
        array[rows, cols] = np.random.random(n)

        df = pd.DataFrame(array)
        df.fillna(method='ffill', axis=0, inplace=True)
        total = df.sum(axis=1)

        ret = total.values
        ret /= ret.max()
        return self.noise_ampl * ret

    def update_noise_type(self, t):
        self.noise_type=t
        self.text_ntype.configure(text='Noise type is '+t)
        self.update_graph_handler()

    def update_noise_ampl(self, a):
        self.noise_ampl = float(a)
        self.text_n.configure(text=('Noise amplitude = ' + str(self.noise_ampl)))
        self.update_graph_handler()

    def add_filter(self):
        if self.filter_type == 'lowpass':
            self.lowpass_filter()
        elif self.filter_type == 'highpass':
            self.highpass_filter()
        elif self.filter_type == 'bandpass':
            self.bandpass_filter()
        elif self.filter_type == 'smoothing':
            self.smoothing_filter()

    def lowpass_filter(self):
        nyq = self.sampling_rate * 0.5
        low = self.low_cutoff / nyq
        b, a = signal.butter(FILTER_ORDER, low, btype='lowpass')
        y = signal.filtfilt(b, a, self.samples)
        self.samples = y

    def highpass_filter(self):
        nyq = self.sampling_rate * 0.5
        high = self.high_cutoff / nyq
        b, a = signal.butter(FILTER_ORDER, high, btype='highpass')
        y = signal.filtfilt(b, a, self.samples)
        self.samples = y

    def bandpass_filter(self):
        nyq = self.sampling_rate * 0.5
        low = self.low_cutoff / nyq
        high = self.high_cutoff / nyq
        b, a = signal.butter(FILTER_ORDER, [low, high], btype='band')
        y = signal.filtfilt(b, a, self.samples)
        self.samples = y

    def smoothing_filter(self):
        y = signal.savgol_filter(self.samples, WINDOW_SIZE, FILTER_ORDER)
        self.samples = y

    def update_filter_type(self, t):
        self.filter_type=t
        self.text_ftype.configure(text='Filter type is '+t)
        self.update_graph_handler()

    def update_graph_freq(self, f):
        # update frequency and its text
        self.freq = MIN_FREQ * 2**float(f)
        self.text_f.configure(text=('Frequency f = ' + str(round(self.freq, 2))))
        self.update_graph_handler()

    def update_graph_ampl(self, a):
        # update amplitude and its text
        self.ampl = float(a)
        self.text_a.configure(text=('Amplitude a = ' + str(self.ampl)))
        self.update_graph_handler()

    def normalize_samples(self):
        if self.samples.max() != 0:
            self.samples /= self.samples.max()

    def save_to_wav(self):
        data = np.iinfo(np.int16).max * self.samples
        samplerate = self.sampling_rate
        wavfile.write("fixed_freq.wav", samplerate, data)

    def update_graph_handler(self):
        # update samples
        # self.samples = np.zeros(SAMPLING_RATE*DURATION)
        self.samples = self.ampl * np.sin(2 * np.pi * self.freq * self.time_axis).astype(np.float32)
        self.add_noise()
        self.add_filter()
        self.normalize_samples()
        # self.save_to_wav()
        self.update_graph()

    def update_graph(self):
        # TODO: Make these plots look better
        # print(self.ampl * self.samples[:10])
        self.a.clear()
        self.a.plot(self.time_axis[:NUM_SAMPLES_TO_PLOT], self.samples[:NUM_SAMPLES_TO_PLOT])
        self.a.set_title('Time Domain Plot')
        self.a.set_xlabel('Time (s)')
        self.a.set_ylabel('Amplitude')

        self.fft.clear()
        self.fft.set_title('Frequency Domain Plot')

        if self.ampl != 0:
            yf = fftpack.fft(self.samples[:self.sampling_rate])
            # d = len(yf)//2
            # self.fft.plot(abs(yf[:(d-1)]))

            # https://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
            # truncate the FFT
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
        sd.play(self.samples, self.sampling_rate)

if __name__ == "__main__":
    app = FixedFrequencyPlayer()

    def on_closing():
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

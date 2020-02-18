'''
    Required Packages: numpy, pandas, scipy, tkinter, pyaudio, matplotlib
'''
import math
import random
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy import signal
import tkinter as tk
from tkinter import ttk
import pyaudio
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# GLOBAL PARAMETERS
LARGE_FONT = ("Verdana", 12)
# sample params
SAMPLING_RATE = 44100
DURATION = 1.0
NUM_SAMPLES_TO_PLOT = 1000
# filter params
FILTER_ORDER = 3
LOWPASS_FREQ = 200
HIGHPASS_FREQ = 800
# fft params
FFT_MAX_FREQ = 2500

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
            self.amplitude_sliders.append(tk.Scale(self, orient=tk.VERTICAL, from_=1, to=0, digits=3, resolution=0.01, showvalue=False, command=lambda a, index=i: self.update_graph_ampl(a, index)))
            self.amplitude_sliders[i].set(0.0)
        # Initialize to A minor chord because I want to die
        self.amplitude_sliders[0].set(1.0)
        self.amplitude_sliders[3].set(1.0)
        self.amplitude_sliders[7].set(1.0)
        self.amplitude_sliders[12].set(1.0)

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

        # Some internal states
        self.samples = np.zeros((200, 1))
        self.noise_type = 'none'
        self.noise_ampl = 0.5
        self.filter_type = 'none'
        self.ampl = []
        self.freq = []
        for i in range(13):
            self.ampl.append(self.amplitude_sliders[i].get())
            self.freq.append(440.0 * math.pow(2, i/12))
        self.volume = 0.8
        self.low_cutoff = LOWPASS_FREQ
        self.high_cutoff = HIGHPASS_FREQ
        self.sampling_rate = SAMPLING_RATE # Hz
        self.duration = DURATION # 1 Second

        # OTHER STUFF
        self.n = np.arange(self.sampling_rate * self.duration)
        self.time_axis = self.n / (self.sampling_rate * self.duration)

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.draw()

        # GRIDS
        label.grid(row=0, column=0, columnspan=14)
        self.text_a.grid(row=1, column=0, columnspan=14)
        for i in range(13):
            self.amplitude_sliders[i].grid(row=2, column=i, columnspan=1)

        self.text_ntype.grid(row=3, column=0, columnspan=6)
        self.noise_n_btn.grid(row=4, column=0, columnspan=2)
        self.noise_w_btn.grid(row=4, column=2, columnspan=2)
        self.noise_p_btn.grid(row=4, column=4, columnspan=2)

        self.text_n.grid(row=3, column=6, columnspan=3)
        noise_slider.grid(row=3, column=9, columnspan=5)
        text_volume.grid(row=4, column=6, columnspan=3)
        volume_slider.grid(row=4, column=9, columnspan=5)

        self.text_ftype.grid(row=5, column=0, columnspan=6)
        self.text_low_cutoff.grid(row=5, column=6, columnspan=2)
        self.text_high_cutoff.grid(row=5, column=8, columnspan=2)
        self.button_update_cutoff.grid(row=5, column=11, columnspan=3)
        
        self.filter_n_btn.grid(row=6, column=0, columnspan=3)
        self.filter_l_btn.grid(row=6, column=3, columnspan=3)
        self.filter_h_btn.grid(row=6, column=6, columnspan=3)
        self.filter_b_btn.grid(row=6, column=9, columnspan=3)
        random_button.grid(row=7, column=0, columnspan=13)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=13)
        self.canvas._tkcanvas.grid(row=9, column=0, columnspan=13)

    def add_noise(self, samples):
        # Choose noise type
        if self.noise_type == 'none':
            return samples
        elif self.noise_type == 'white':
            noise = self.white_noise()
        elif self.noise_type == 'pink':
            noise = self.pink_noise()

        # Add noise to samples
        samples += noise

        # TODO: Normalize to maximum value of 1 (?)
        # samples /= self.samples.max()
        return samples

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
        self.text_n.configure(text=('amp = ' + str(self.noise_ampl)))
        self.update_graph_handler()

    def add_filter(self, samples):
        if self.filter_type == 'lowpass':
            return self.lowpass_filter(samples)
        elif self.filter_type == 'highpass':
            return self.highpass_filter(samples)
        elif self.filter_type == 'bandpass':
            return self.bandpass_filter(samples)

        return samples

    def lowpass_filter(self, xn):
        nyq = self.sampling_rate * 0.5
        low = self.low_cutoff / nyq
        b, a = signal.butter(FILTER_ORDER, low, btype='lowpass')
        y = signal.filtfilt(b, a, xn)
        return y

    def highpass_filter(self, xn):
        nyq = self.sampling_rate * 0.5
        high = self.high_cutoff / nyq
        b, a = signal.butter(FILTER_ORDER, high, btype='highpass')
        y = signal.filtfilt(b, a, xn)
        return y

    def bandpass_filter(self, xn):
        nyq = self.sampling_rate * 0.5
        low = self.low_cutoff / nyq
        high = self.high_cutoff / nyq
        b, a = signal.butter(FILTER_ORDER, [low, high], btype='band')
        y = signal.filtfilt(b, a, xn)
        # print(xn[:20])
        # print(y[:20])
        return y

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

        self.low_cutoff, self.high_cutoff = l, h
        self.update_graph_handler()

    def update_volume(self, v):
        self.volume = v
        print(self.volume)

    def update_graph_ampl(self, a, i):
        # update amplitudes
        self.ampl[i] = float(a)
        self.update_graph_handler()

    def update_graph_handler(self):
        # update samples
        self.samples = np.zeros(int(SAMPLING_RATE*DURATION)).astype(np.float32)
        for i in range(13):
            self.samples += self.ampl[i] * np.sin(2 * np.pi * self.freq[i] * self.time_axis).astype(np.float32)
        if any(a > 0.0 for a in self.ampl):
            self.samples /= self.samples.max() # normalize
        self.samples = self.add_noise(self.samples)
        self.samples = self.add_filter(self.samples)
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
        if any(s > 0.0 for s in self.samples):
            yf = fftpack.fft(self.samples)
            # d = len(yf)//2
            # self.fft.plot(abs(yf[:(d-1)]))

            # https://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python
            # truncate the FFT
            yf = yf[:FFT_MAX_FREQ*2]
            yp = np.abs(yf) ** 2
            fft_freq = fftpack.fftfreq(len(yp), 1/(FFT_MAX_FREQ*2))
            i = fft_freq>0
            self.fft.plot(fft_freq[i], 10*np.log10(yp[i]))
            self.fft.set_xlabel('Frequency Hz')
            self.fft.set_ylabel('PSD (dB)')

        self.fft.set_title('Frequency Domain Plot')
        self.canvas.draw()

    def update_random(self):
        for i in range(13):
            # offset = (random.random()*2-1) * 0.5
            # self.ampl[i] += offset
            # if self.ampl[i] > 1.0:
            #     self.ampl[i] = 1.0
            # elif self.ampl[i] < 0.0:
            #     self.ampl[i] = 0.0
            self.amplitude_sliders[i].set(random.random())

if __name__ == "__main__":
    app = MultiFrequencyPlayer()

    def on_closing():
        app.quit()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

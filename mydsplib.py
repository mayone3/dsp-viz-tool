import math
import random
import numpy as np
import pandas as pd
from scipy import fftpack
from scipy import signal
from scipy.io import wavfile

# audio params
SAMPLE_RATE = 44100
DURATION = 2.0
# filter params
FILTER_ORDER = 3
CUTOFF = 1000
BAND = [440, 880]
WINDOW_SIZE = 51

def add_noise(sample, type, amplitude, sample_rate=SAMPLE_RATE, duration=DURATION):
    if type == 'white':
        sample += white_noise(amplitude, sample_rate, duration)
    elif type == 'pink':
        sample += pink_noise(amplitude, sample_rate, duration)
    return sample

def white_noise(amplitude, sample_rate=SAMPLE_RATE, duration=DURATION):
    return amplitude * (np.random.random(int(sample_rate * duration))*2-1).astype(np.float32)

'''
source: https://scicomp.stackexchange.com/questions/18987/algorithm-for-high-quality-1-f-noise
source: https://stackoverflow.com/questions/33933842/how-to-generate-noise-in-frequency-range-with-numpy
source*: https://www.dsprelated.com/showarticle/908.php
'''
def pink_noise(amplitude, sample_rate=SAMPLE_RATE, duration=DURATION, ncols=16):
    """Generates pink noise using the Voss-McCartney algorithm.

    nrows: number of values to generate
    ncols: number of random sources to add

    returns: NumPy array
    """
    nrows = int(sample_rate * duration)
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
    return amplitude * ret

def add_filter(sample, type='none', cutoff=CUTOFF, band=BAND, filter_order=FILTER_ORDER, window_size=WINDOW_SIZE, sample_rate=SAMPLE_RATE):
    if type == 'lowpass':
        sample = lowpass_filter(sample, cutoff, sample_rate, filter_order)
    elif type == 'highpass':
        sample = highpass_filter(sample, cutoff, sample_rate, filter_order)
    elif type == 'bandpass':
        sample = bandpass_filter(sample, band, sample_rate, filter_order)
    elif type == 'smoothing':
        sample = smoothing_filter(sample, window_size, filter_order)
    return sample

def lowpass_filter(sample, cutoff, sample_rate, filter_order):
    nyq = sample_rate * 0.5
    _cutoff = cutoff / nyq
    b, a = signal.butter(filter_order, _cutoff, btype='lowpass')
    y = signal.filtfilt(b, a, sample)
    return y

def highpass_filter(sample, cutoff, sample_rate, filter_order):
    nyq = sample_rate * 0.5
    _cutoff = cutoff / nyq
    b, a = signal.butter(filter_order, _cutoff, btype='highpass')
    return signal.filtfilt(b, a, sample)

def bandpass_filter(sample, band, sample_rate, filter_order):
    nyq = sample_rate * 0.5
    _band = [(f / nyq) for f in band]
    b, a = signal.butter(filter_order, _band, btype='band')
    return signal.filtfilt(b, a, sample)

def smoothing_filter(sample, window_size, filter_order):
    return signal.savgol_filter(sample, window_size, filter_order)

def am(sample_data, sample_carrier):
    return (sample_data+1) * sample_carrier

def fm(sample_baseband, ts, f_m, f_c, f_dev):
    # return am(sample_data, sample_carrier)
    '''
    https://en.wikipedia.org/wiki/Frequency_modulation

    Frequency Modulation:
        y(t) = A_c * cos( 2*pi * f_c * t + 2*pi * f_dev * int_0^t x_m(\tau) d\tau )

    For sinusoid baseband signal:
        int_0^t x_m(\tau) d\tau = A_m * sin( 2*pi * f_m * t ) / ( 2*pi * f_m )

        y(t) = A_c * cos( 2*pi * f_c * t + ( A_m * f_dev / f_m ) * sin( 2*pi * f_m * t ) )

    For simplicity, we have
        A_c = 1, A_m = 1

    Therefore,
        y(t) = cos( 2*pi * f_c * t + ( f_dev / f_m ) * sin( 2*pi * f_m * t ) )
    '''
    return np.cos( 2*np.pi * f_c * ts + (f_dev / f_m) * np.sin( 2*pi * f_m * ts ) ).astyle(np.float32)

def normalize_sample(sample):
    if sample.max() != 0:
        sample /= sample.max()
    return sample

def save_to_wav(sample, filename='audio.wav', sample_rate=SAMPLE_RATE):
    data = np.iinfo(np.int16).max * sample
    wavfile.write(filename, sample_rate, data)

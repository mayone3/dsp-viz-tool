import numpy as np
import sounddevice as sd

# Play an 440 Hz Tone
# TODO: Make this non-blocking
# Intergrate this with the rest of the project

fs = 44100
f = 440.0
duration = 10.0
t = np.linspace(0, duration, duration * fs, False)

tone = np.sin(f * t * 2 * np.pi)

sd.play(tone, fs)
# Make this non-blocking
sd.wait()

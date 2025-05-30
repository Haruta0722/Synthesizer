import numpy as np

class Oscillator:
    def __init__(self, wave_type=0, fm_amp=0.0, fm_freq=0.0, detune=0.0, rate=44100):
        self.wave_type = wave_type
        self.fm_amp = fm_amp
        self.fm_freq = fm_freq
        self.detune = detune
        self.rate = rate

    def generate(self, pitch, pos, x):
        t = (pitch * (1 + self.detune)) * (x + pos) / self.rate
        t = t - np.floor(t)

        if self.wave_type == 1:
            wave = t * 2.0 - 1.0
        elif self.wave_type == 2:
            wave = np.where(t <= 0.5, -1.0, 1.0)
        elif self.wave_type == 3:
            wave = np.abs(t * 2.0 - 1.0) * 2.0 - 1.0
        elif self.wave_type == 4:
            wave = np.sin(2.0 * np.pi * t + self.fm_amp * np.sin(2.0 * np.pi * t * self.fm_freq))
        else:
            wave = np.sin(2.0 * np.pi * t)

        return wave
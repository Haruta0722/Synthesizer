# synth_state.py
import numpy as np

class SynthState:
    def __init__(self):
        self.sl = np.array([
            0, 150, 150, 200,  # wave, attack, release, LPF_cutoff
            0, 0,              # FM_amp, FM_freq
            1, 0,              # Unison, Detune
            0, 0               # Osc2 wave, detune
        ])
        self.keyon = 0
        self.pre_keyon = 0
        self.pitch = 440
        self.velosity = 0.0
        self.playing = True
        self.bufsize = 32
        self.rate = 44100
        self.prev_filter_y = 0.0  # ローパスフィルター用
        self.lpfbuf = [0.0, 0.0, 0.0, 0.0]
        self.outwave = np.zeros(self.bufsize, dtype=np.float32)
        self.filter_env_val = 0.0
        self.filter_env_phase = 'idle'
        self.filter_env_pos = 0.0
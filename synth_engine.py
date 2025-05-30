from oscillator import Oscillator
from filter import lowpass
import numpy as np

def synthesize(state, pos, x):
    sl = state.sl
    pitch = state.pitch
    keyon = state.keyon
    velosity = state.velosity
    bufsize = state.bufsize
    RATE = state.rate

    wave_total = np.zeros_like(x, dtype=np.float32)

    # === Oscillator 1 (with unison) ===
    unison_count = max(1, sl[6])
    detune_amt = sl[7] / 1000.0
    for i in range(unison_count):
        detune = (i - (unison_count - 1) / 2) * detune_amt
        osc1 = Oscillator(
            wave_type=sl[0],
            fm_amp=sl[4] / 100.0,
            fm_freq=sl[5],
            detune=detune,
            rate=RATE
        )
        wave_total += osc1.generate(pitch, pos, x)

    wave_total /= unison_count

    # === Oscillator 2 ===
    osc2 = Oscillator(
        wave_type=sl[8],
        detune=sl[9] / 1000.0,
        rate=RATE
    )
    wave_total += osc2.generate(pitch, pos, x)

    wave_total /= 2.0  # オシレーター合成後に平均化

    # === Envelope ===
    pos += bufsize
    f_attack = sl[10] / 1000.0
    f_decay = sl[11] / 1000.0
    f_sustain = sl[12] / 255.0
    f_release = sl[13] / 1000.0
    if keyon == 1:
        vels = velosity + x * ((sl[1] / 1000)**3 + 0.00001)
        vels[vels > 0.6] = 0.6
        if state.filter_env_phase in ('idle', 'release'):
            state.filter_env_phase = 'attack'
            state.filter_env_pos = 0.0

    if state.filter_env_phase == 'attack':
        state.filter_env_val += 1.0 / (f_attack * RATE / state.bufsize)
        if state.filter_env_val >= 1.0:
            state.filter_env_val = 1.0
            state.filter_env_phase = 'decay'
    elif state.filter_env_phase == 'decay':
        state.filter_env_val -= (1.0 - f_sustain) / (f_decay * RATE / state.bufsize)
        if state.filter_env_val <= f_sustain:
            state.filter_env_val = f_sustain
            state.filter_env_phase = 'sustain'
    else:
        vels = velosity - x * ((sl[2] / 1000)**3 + 0.00001)
        vels[vels < 0.0] = 0.0
        if state.filter_env_phase != 'idle':
            state.filter_env_phase = 'release'
        if state.filter_env_phase == 'release':
            state.filter_env_val -= f_sustain / (f_release * RATE / state.bufsize)
        if state.filter_env_val <= 0:
            state.filter_env_val = 0
            state.filter_env_phase = 'idle'
    state.velosity = vels[-1]
    # ベースカットオフとエンベロープの合成
    base_cutoff = sl[3] / 255.0
    mod_cutoff = base_cutoff + state.filter_env_val * (1.0 - base_cutoff)
    cutoff_freq = mod_cutoff * (RATE / 2)
        # === Apply Envelope to Oscillator output ===
    signal = vels * wave_total

    # === Apply Lowpass Filter ===
    if not hasattr(state, "lpfbuf"):
        state.lpfbuf = [0.0, 0.0, 0.0, 0.0]
        state.outwave = np.zeros(state.bufsize, dtype=np.float32)

    # フィルター適用
    filtered, state.lpfbuf = lowpass(
        signal, cutoff_freq, RATE, bufsize, state.lpfbuf, state.outwave
    )

    return filtered, pos
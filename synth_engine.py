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

    wave_total /= 2.0  # 平均化

    # === エンベロープ処理 ===
    pos += bufsize
    atk = (sl[1] / 1000)**3 + 0.00001
    rel = (sl[2] / 1000)**3 + 0.00001

    # 状態遷移処理
    if keyon == 1 and state.pre_keyon == 0:
        state.env_phase = "attack"
    elif keyon == 0 and state.pre_keyon == 1:
        state.env_phase = "release"

    # エンベロープ生成
    if state.env_phase == "attack":
        vels = state.velosity + x * atk
        vels[vels > 0.6] = 0.6
        if vels[-1] >= 0.6:
            state.env_phase = "sustain"

    elif state.env_phase == "sustain":
        if keyon == 0:
            state.env_phase = "release"  # ←★重要: key離した瞬間にreleaseへ
            vels = state.velosity - x * rel
        else:
            vels = np.ones_like(x) * state.velosity

    elif state.env_phase == "release":
        vels = state.velosity - x * rel
        vels[vels < 0.0] = 0.0
        if vels[-1] <= 0.0:
            state.env_phase = "off"

    else:  # env_phase == "off"
        vels = np.zeros_like(x)

    # 状態更新
    state.velosity = vels[-1]
    state.pre_keyon = keyon

    wave_total *= vels #フィルター適用

    # === Lowpass Filter ===
    # スライダー値取得
    cutoff_val = sl[3]

    # フィルター適用
    filtered, state.lpfbuf = lowpass(
        wave_total, cutoff_val, RATE, bufsize, state.lpfbuf, state.outwave
    )

    return filtered, pos

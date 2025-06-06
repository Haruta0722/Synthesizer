from oscillator import Oscillator
from filter import lowpass, lowpass_dynamic_cutoff_interp
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

    fenv_amt = sl[10] / 255.0  # 深さ
    fenv_atk = (sl[11] / 1000.0)**3 + 0.00001
    fenv_rel = (sl[12] / 1000.0)**3 + 0.00001

    fenv = np.zeros_like(x)

    if state.env_phase == "attack":
        # 音量エンベロープ
        vels = state.velosity + x * atk
        vels[vels > 0.6] = 0.6
        if vels[-1] >= 0.6:
            state.env_phase = "sustain"

        # フィルターエンベロープ
        fenv = state.fenv_value + x * fenv_atk
        fenv[fenv > 1.0] = 1.0
        if fenv[-1] >= 1.0:
            state.env_phase = "sustain"

    elif state.env_phase == "sustain":
        if keyon == 0:
            state.env_phase = "release"  # ←★重要: key離した瞬間にreleaseへ
            vels = state.velosity - x * rel
            fenv = state.fenv_value - x * fenv_rel
        else:
            vels = np.ones_like(x) * state.velosity
            fenv = np.ones_like(x)
        

    elif state.env_phase == "release":
        vels = state.velosity - x * rel
        vels[vels < 0.0] = 0.0
        fenv = state.fenv_value - x * fenv_rel
        fenv[fenv < 0.0] = 0.0
        if vels[-1] <= 0.0:
            state.env_phase = "off"

    else:  # env_phase == "off"
        vels = np.zeros_like(x)

    # 状態更新
    state.velosity = vels[-1]
    state.fenv_value = fenv[-1]
    state.pre_keyon = keyon
    # === Lowpass Filter ===
    # スライダー値取得
    # 基本のカットオフ値
    base_cutoff = int(sl[3])
    cutoff_val = np.clip(base_cutoff + (fenv) * fenv_amt * 255, 0, 255)

    filtered, state.lpfbuf = lowpass_dynamic_cutoff_interp(
        wave_total, cutoff_val, RATE, state.lpfbuf
    )
    print(vels[:10])
    print(fenv[:10])
    # 最後にボリュームエンベロープ適用
    filtered *= vels
    state.fenv_curve = fenv.copy()
    return filtered, pos

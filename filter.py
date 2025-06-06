import numpy as np

def lowpass(wave, cutoff_slider_val, RATE, bufsize, lpfbuf, outwave):
    # 安全化
    wave = np.nan_to_num(wave)
    wave = np.clip(wave, -1.0, 1.0)

    # フィルター係数の計算
    w0 = 2.0 * np.pi * (200 + (cutoff_slider_val / 255.0) ** 2 * 20000) / RATE
    Q = 1.0
    alpha = np.sin(w0) / (2.0 * Q)
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0) / a0
    a2 = (1 - alpha) / a0
    b0 = (1 - np.cos(w0)) / 2 / a0
    b1 = (1 - np.cos(w0)) / a0
    b2 = (1 - np.cos(w0)) / 2 / a0

    for i in range(bufsize):
        try:
            out = (
                b0 * wave[i]
                + b1 * lpfbuf[1]
                + b2 * lpfbuf[0]
                - a1 * lpfbuf[3]
                - a2 * lpfbuf[2]
            )
            outwave[i] = np.clip(out, -1.0, 1.0)  # セーフクリップ
        except Exception:
            outwave[i] = 0.0

        # フィードバック更新
        lpfbuf[0] = lpfbuf[1]
        lpfbuf[1] = wave[i]
        lpfbuf[2] = lpfbuf[3]
        lpfbuf[3] = outwave[i]

    return outwave, lpfbuf


def lowpass_dynamic_cutoff_interp(wave, cutoff_array, RATE, lpfbuf, update_every=32):
    outwave = np.zeros_like(wave)
    length = len(wave)

    # フィルター係数を保存する
    b0s = np.zeros(length)
    b1s = np.zeros(length)
    b2s = np.zeros(length)
    a1s = np.zeros(length)
    a2s = np.zeros(length)

    for i in range(0, length, update_every):
        # 現在と次のカットオフ値
        c0 = cutoff_array[i]
        c1 = cutoff_array[min(i + update_every, length - 1)]

        # 現在と次のフィルター係数を計算
        def compute_coeff(cutoff_val):
            freq = 200 + (cutoff_val / 255.0)**2 * 20000
            w0 = 2.0 * np.pi * freq / RATE
            Q = 1.0
            alpha = np.sin(w0) / (2.0 * Q)
            a0 = 1 + alpha
            a1 = -2 * np.cos(w0) / a0
            a2 = (1 - alpha) / a0
            b0 = (1 - np.cos(w0)) / 2 / a0
            b1 = (1 - np.cos(w0)) / a0
            b2 = (1 - np.cos(w0)) / 2 / a0
            return b0, b1, b2, a1, a2

        b0_0, b1_0, b2_0, a1_0, a2_0 = compute_coeff(c0)
        b0_1, b1_1, b2_1, a1_1, a2_1 = compute_coeff(c1)

        for j in range(update_every):
            idx = i + j
            if idx >= length:
                break
            t = j / update_every
            b0s[idx] = (1 - t) * b0_0 + t * b0_1
            b1s[idx] = (1 - t) * b1_0 + t * b1_1
            b2s[idx] = (1 - t) * b2_0 + t * b2_1
            a1s[idx] = (1 - t) * a1_0 + t * a1_1
            a2s[idx] = (1 - t) * a2_0 + t * a2_1

    # フィルター適用（IIR）
    for i in range(length):
        out = (
            b0s[i] * wave[i]
            + b1s[i] * lpfbuf[1]
            + b2s[i] * lpfbuf[0]
            - a1s[i] * lpfbuf[3]
            - a2s[i] * lpfbuf[2]
        )
        out = np.clip(out, -1.0, 1.0)
        outwave[i] = out

        # 更新（過去の値）
        lpfbuf[0] = lpfbuf[1]
        lpfbuf[1] = wave[i]
        lpfbuf[2] = lpfbuf[3]
        lpfbuf[3] = out

    return outwave, lpfbuf
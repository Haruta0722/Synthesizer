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
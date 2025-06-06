import numpy as np
import cv2

# スライダーの名前
slName = np.array([
    'Wave_type1', 'Attack', 'Release', 'Lowpass_freq',
    'FM_amp1', 'FM_freq1', 'Unison1', 'Detune1',
    'Wave_type2', 'Detune2',
    'FilterEnvAmt', 'FilterEnvAtk', 'FilterEnvRel'  # ←追加
])

# 鍵盤のサイズ
ksx, ksy = 800, 200

# 白鍵と黒鍵のインデックス
highkeys = np.array([0,1,1,3,3,4,5,6,6,8,8,10,10,11, 12,13,13,15,15,16,17,18,18,20,20,22,22,23, 24,24])
lowkeys  = np.array([0,2,4,5,7,9,11, 12,14,16,17,19,21,23, 24])

def changeBar(val, state):
    for i in range(len(slName)):
        state.sl[i] = cv2.getTrackbarPos(slName[i], "keyboard")

def setup_gui_and_keyboard(state):
    assert len(state.sl) == len(slName), "state.sl の要素数が slName と一致していません"

    # キーボード画像作成
    keyboard = np.ones((ksy, ksx, 3), dtype=np.uint8) * 255

    # 白鍵
    for i in range(15):
        cv2.rectangle(keyboard, (int(ksx / 15 * i), 0), (int(ksx / 15 * (i + 1)), ksy), (0, 0, 0), 5)

    # 黒鍵
    for i in range(15):
        if i in {0, 1, 3, 4, 5, 7, 8, 10, 11, 12}:
            cv2.rectangle(
                keyboard,
                (int(ksx / 15 * i + ksx / 27), 0),
                (int(ksx / 15 * (i + 1) + ksx / 33), int(ksy / 2)),
                (0, 0, 0), -1
            )

    # GUIウィンドウ初期化
    cv2.namedWindow("keyboard", cv2.WINDOW_NORMAL)

    # スライダー登録
    for i in range(len(slName)):
        if slName[i] == 'FM_freq1':
            max_val = 11
        elif slName[i] == 'Wave_type1' or slName[i] == 'Wave_type2':
            max_val = 4
        elif slName[i] == 'Unison1':
            max_val = 8
        elif slName[i] == 'Detune1' or slName[i] == 'Detune2':
            max_val = 100
        #elif slName[i] == 'FilterEnvAmt':
            #max_val = 1
        else:
            max_val = 255

        cv2.createTrackbar(slName[i], "keyboard", state.sl[i], max_val,
                           lambda val, i=i: changeBar(val, state))
        cv2.setTrackbarPos(slName[i], "keyboard", state.sl[i])

    # マウスイベント登録
    def mouse_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("Mouse click detected!")  # ← デバッグ
            state.keyon = 1
            if y >= ksy / 2:
                note = lowkeys[int(15.0 * x / ksx)]
            else:
                note = highkeys[int(30.0 * x / ksx)]
            state.pitch = 440 * np.power(2, (note - 9) / 12)

        elif event == cv2.EVENT_LBUTTONUP:
            state.keyon = 0

        # pre_keyon の更新は synthesize() 内で行うのでここでは不要

    cv2.setMouseCallback("keyboard", mouse_event)

    return keyboard

def draw_filter_env(state):
    width = 400
    height = 200
    img = np.ones((height, width, 3), dtype=np.uint8) * 255

    # エンベロープ値
    fenv = state.fenv_curve
    if len(fenv) == 0:
        return

    # エンベロープを青線で描画
    xs = np.linspace(0, width - 1, len(fenv)).astype(int)
    ys_fenv = (1.0 - fenv) * (height - 1)  # 上が1.0、下が0.0になるように

    for i in range(len(fenv) - 1):
        pt1 = (xs[i], int(ys_fenv[i]))
        pt2 = (xs[i+1], int(ys_fenv[i+1]))
        cv2.line(img, pt1, pt2, (255, 0, 0), 2)  # 青線

    # --- カットオフ推移をオーバーレイ ---
    # fenv から実際のカットオフ値を計算（スライダー値と係数反映）
    base_cutoff = state.sl[3]
    fenv_amt = state.sl[10] / 255.0
    cutoff_vals = np.clip(base_cutoff + fenv * fenv_amt * 255, 0, 255)

    # スケーリング：cutoff_slider_val → Hz → log表示
    freqs = 200 + (cutoff_vals / 255.0)**2 * 20000
    log_freqs = np.log10(freqs)
    min_log = np.log10(200)
    max_log = np.log10(20200)
    ys_cutoff = (1.0 - (log_freqs - min_log) / (max_log - min_log)) * (height - 1)

    for i in range(len(ys_cutoff) - 1):
        pt1 = (xs[i], int(ys_cutoff[i]))
        pt2 = (xs[i+1], int(ys_cutoff[i+1]))
        cv2.line(img, pt1, pt2, (0, 0, 255), 2)  # 赤線

    # 凡例追加（オプション）
    cv2.putText(img, "Filter Env (Blue)", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
    cv2.putText(img, "Cutoff Freq (Red)", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

    cv2.imshow("Filter Envelope", img)
import numpy as np
import cv2

# スライダーの名前
slName = np.array([
    'Wave_type1', 'Attack', 'Release', 'Lowpass_freq',
    'FM_amp1', 'FM_freq1', 'Unison1', 'Detune1',
    'Wave_type2', 'Detune2',
    'F_Atk', 'F_Dcy', 'F_Sus', 'F_Rel'  # ← 追加
])

# 鍵盤のサイズ
ksx, ksy = 800, 200

# 白鍵と黒鍵のインデックス
highkeys = np.array([0,1,1,3,3,4,5,6,6,8,8,10,10,11, 12,13,13,15,15,16,17,18,18,20,20,22,22,23, 24,24])
lowkeys  = np.array([0,2,4,5,7,9,11, 12,14,16,17,19,21,23, 24])

def changeBar(val, state):
     for i in range(len(slName)):  # 固定値8をやめる
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
            cv2.rectangle(keyboard,
                          (int(ksx / 15 * i + ksx / 27), 0),
                          (int(ksx / 15 * (i + 1) + ksx / 33), int(ksy / 2)),
                            (0, 0, 0), -1)

    # GUIウィンドウ初期化
    cv2.namedWindow("keyboard", cv2.WINDOW_NORMAL)

    # スライダー登録
    for i in range(len(slName)):
        if slName[i] == 'FM_freq':
            max_val = 11
        elif slName[i] == 'Wave_type1' or slName[i] == 'Wave_type2':
            max_val = 4
        elif slName[i] == 'Unison1' or slName[i] == 'Unison2':
            max_val = 8
        elif slName[i] == 'Detune1' or slName[i] == 'Detune2':
            max_val = 100
        else:
            max_val = 255
        cv2.createTrackbar(slName[i], "keyboard", state.sl[i], max_val,
                        lambda val, i=i: changeBar(val, state))
        cv2.setTrackbarPos(slName[i], "keyboard", state.sl[i])

    # マウスイベント登録
    def mouse_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            state.keyon = 1
            if y >= ksy / 2:
                note = lowkeys[int(15.0 * x / ksx)]
            else:
                note = highkeys[int(30.0 * x / ksx)]
            state.pitch = 440 * np.power(2, (note - 9) / 12)
        elif event == cv2.EVENT_LBUTTONUP:
            state.keyon = 0

        if state.pre_keyon == 0 and state.keyon == 1:
            state.velosity = 0.0
        state.pre_keyon = state.keyon

    cv2.setMouseCallback("keyboard", mouse_event)

    return keyboard
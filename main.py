import threading
import cv2
from synth_state import SynthState
from audio_play import audioplay
from gui_controls import setup_gui_and_keyboard, draw_filter_env

if __name__ == "__main__":
    state = SynthState()

    # GUI初期化
    keyboard = setup_gui_and_keyboard(state)

    # 音声再生スレッド
    thread = threading.Thread(target=audioplay, args=(state,))
    thread.start()

    while True:
        draw_filter_env(state)
        cv2.imshow("keyboard", keyboard)
        k = cv2.waitKey(100) & 0xFF
        if k == ord('q'):
            state.playing = False
            break

    cv2.destroyAllWindows()
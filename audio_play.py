import pyaudio
import struct
import numpy as np
from synth_engine import synthesize

def audioplay(state):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=state.rate,
                    frames_per_buffer=state.bufsize,
                    output=True)
    pos = 0
    x = np.arange(state.bufsize)

    # 修正: stream.is_active() は使わない
    while state.playing:
        buf, pos = synthesize(state, pos, x)
        buf = np.nan_to_num(buf)  # NaN, Inf を 0 に
        buf = np.clip(buf, -1.0, 1.0)  # 正規化された float 音声をクリップ
        buf = (buf * 32767).astype(np.int16)
        # 書き込み
        stream.write(struct.pack("h" * len(buf), *buf))

    stream.stop_stream()
    stream.close()
    p.terminate()
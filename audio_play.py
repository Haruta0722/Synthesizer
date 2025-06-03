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

    while stream.is_active() and state.playing:
        buf, pos = synthesize(state, pos, x)
        buf = (buf * 32768.0).astype(np.int16)
        stream.write(struct.pack("h" * len(buf), *buf))

    stream.stop_stream()
    stream.close()
    p.terminate()
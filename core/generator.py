import zlib
import time
import random
import hashlib
import os

class Generator:
    def __init__(self, source):
        self.src = source

    def generate_stub(self):
        entropy = int(time.perf_counter() * 1000) & 0xFFFFFFFF
        compressed = zlib.compress(self.src.encode())

        return f'''
import zlib, time, random, os

def _run():
    _seed = (os.getpid() ^ {entropy}) & 0xFFFFFFFF

    _data = {compressed!r}

    _r = list(range(256))
    random.seed(_seed)
    random.shuffle(_r)
    _inv = {{v: k for k, v in enumerate(_r)}}

    _out = bytearray()
    for b in zlib.decompress(_data):
        v = _inv[b]
        _out.append(((v << 1) & 0xFF) | (v >> 7))

    exec(bytes(_out), {{'__name__': '__main__'}})

if __name__ == "__main__":
    _run()
'''
import zlib
import time

class Generator:
    def __init__(self, source):
        self.src = source

    def generate_stub(self):
        key = int(time.time_ns()) & 0xFF

        raw = self.src.encode()
        comp = zlib.compress(raw)

        obf = bytearray()
        k = key
        for b in comp:
            r = ((b << 3) | (b >> 5)) & 0xFF   # rotate left
            r ^= k
            obf.append(r)
            k = (k * 7 + 13) & 0xFF           # rolling key

        return f'''
import zlib

def _run():
    data = {bytes(obf)!r}
    key = {key}

    out = bytearray()
    k = key
    for b in data:
        v = b ^ k
        v = ((v >> 3) | (v << 5)) & 0xFF     # rotate right
        out.append(v)
        k = (k * 7 + 13) & 0xFF

    code = zlib.decompress(out)
    exec(code, {{'__name__': '__main__'}})

if __name__ == "__main__":
    _run()
'''

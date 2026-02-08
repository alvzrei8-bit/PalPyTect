import random
import zlib
import time
import hashlib

class Generator:
    def __init__(self, source):
        self.src = source

    def generate_stub(self):
        entropy = int(time.perf_counter() * 1000) & 0xFFFFFFFF
        payload = zlib.compress(self.src.encode())

        return f'''
import os, time, zlib, hashlib, random

def _vmp():
    _hist = []
    _s = (os.getpid() ^ {entropy}) & 0xFFFFFFFF

    _m = {self._gen_map(entropy)}
    _NEXT = {self._kid("NEXT")}
    _BUMP = {self._kid("BUMP")}
    _ptr = {self._kid("ENTRY")}
    _payload = None

    while _ptr in _m:
        _curr = _m.pop(_ptr)
        _t = time.perf_counter_ns()

        try:
            _roll = hashlib.sha256(str(_hist).encode()).digest()
            _seed = _s ^ int.from_bytes(_roll[:4], 'big')

            _r = list(range(256))
            random.seed(_seed)
            random.shuffle(_r)
            _inv = {{v: k for k, v in enumerate(_r)}}

            _raw = bytearray()
            for b in zlib.decompress(_curr):
                v = _inv[b]
                _raw.append(((v << 1) & 0xFF) | (v >> 7))

            _ns = {{}}
            exec(bytes(_raw), _ns)

            if 'PAYLOAD' in _ns:
                _payload = _ns['PAYLOAD']

            _ptr = _ns.get(_NEXT)
            _s = (_s ^ _ns.get(_BUMP, 0) ^ (time.perf_counter_ns() - _t)) & 0xFFFFFFFF
            _hist.append(_ptr)

        except Exception:
            break

    if callable(_payload):
        _payload()

if __name__ == "__main__":
    _vmp()
'''

    def _kid(self, s):
        return int(hashlib.sha256(s.encode()).hexdigest()[:12], 16)

    def _gen_map(self, key):
        blocks = {
            "ENTRY": (
                f"self[{self._kid('NEXT')}]={self._kid('CORE')};"
                f"self[{self._kid('BUMP')}]=1"
            ),
            "CORE": (
                f\"PAYLOAD=lambda:exec(zlib.decompress({zlib.compress(self.src.encode())!r}));"
                f"self[{self._kid('NEXT')}]={self._kid('EXIT')};"
                f"self[{self._kid('BUMP')}]=3\"
            ),
            "EXIT": (
                f"self[{self._kid('NEXT')}]=None;"
                f"self[{self._kid('BUMP')}]=0"
            ),
        }

        m = {}
        state = key
        hist = []

        for name in blocks:
            roll = hashlib.sha256(str(hist).encode()).digest()
            seed = state ^ int.from_bytes(roll[:4], 'big')

            r = list(range(256))
            random.seed(seed)
            random.shuffle(r)

            comp = zlib.compress(blocks[name].encode())
            out = bytearray()
            for b in comp:
                rot = ((b >> 1) | (b << 7)) & 0xFF
                out.append(r[rot])

            m[self._kid(name)] = bytes(out)
            hist.append(self._kid(name))
            state ^= 0x1337

        return m
import random
import zlib
import os
import time
from core.obfuscation import Obfuscator

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.ob = Obfuscator()

    def generate_stub(self):
        initial_key = random.randint(1, 255)
        protected_stub = f"""
import sys, os, time, zlib

def _vmp_ultra():
    _t_start = time.perf_counter_ns()
    _chain = {initial_key}
    _m = {self._generate_chained_map(initial_key)}
    _ptr = "0xENTRY"
    _ns = {{'_v': 0}}
    _steps = 0
    _target = len(_m)

    while _ptr:
        if _ptr not in _m: break
        _curr = _m.pop(_ptr)
        _steps += 1
        try:
            _jitter = time.perf_counter_ns() % 100
            _seed = _chain ^ _jitter
            _r = list(range(256))
            import random as _rnd; _rnd.seed(_seed); _rnd.shuffle(_r)
            _inv = {{v: k for k, v in enumerate(_r)}}
            _raw = bytearray()
            for _b in zlib.decompress(_curr):
                _v = _inv[_b]
                _raw.append(((_v << 1) & 0xFF) | (_v >> 7))
            _co = compile(bytes(_raw), '', 'exec')
            exec(_co, _ns)
            _ptr = _ns.get(170)
            _chain = (_chain ^ _ns.get(187, 0)) % 256
            if (time.perf_counter_ns() - _t_start) / _steps > 10**8:
                _ptr = "0xPOISON"
            _ns.clear()
            _ns['_v'] = _steps
        except Exception:
            _ptr = "0xPOISON"
    if _ns.get('_steps') == _target:
        pass

if __name__ == "__main__":
    _vmp_ultra()
"""
        return protected_stub

    def _generate_chained_map(self, key):
        blocks = {
            "0xENTRY": ["self[170] = '0xWORK'; self[187] = 42", 42],
            "0xWORK": ["self[170] = '0xFIN'; self[187] = 99", 99],
            "0xFIN": ["self[170] = None; self[187] = 0", 0],
            "0xPOISON": ["while True: os.getpid()", 0]
        }
        chained_map = {}
        curr_key = key
        for node in ["0xENTRY", "0xWORK", "0xFIN", "0xPOISON"]:
            code, delta = blocks[node]
            build_seed = curr_key ^ 0 
            sub_map = list(range(256))
            random.seed(build_seed)
            random.shuffle(sub_map)
            compressed = zlib.compress(code.encode())
            transformed = bytearray()
            for b in compressed:
                rotated = ((b >> 1) | (b << 7)) & 0xFF
                transformed.append(sub_map[rotated])
            chained_map[node] = bytes(transformed)
            curr_key = (curr_key ^ delta) % 256
        return chained_map

import random
import zlib
import os
import time
import hashlib
import base64

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts

    def generate_stub(self):
        initial_entropy = int(time.perf_counter() * 1000) & 0xFFFFFFFF
        k_n = self._hash_id("NEXT")
        k_b = self._hash_id("BUMP")
        
        payload_script = f"""
_stack = []
for _op, _arg in {self.bc}:
    if _op == 'V_LDC':
        _stack.append({self.cn}[_arg])
    elif _op == 'V_PRN':
        print(_stack.pop())
    elif _op == 'V_ADD':
        _b = _stack.pop(); _a = _stack.pop()
        _stack.append(_a + _b)
    elif _op == 'V_SUB':
        _b = _stack.pop(); _a = _stack.pop()
        _stack.append(_a - _b)
    elif _op == 'V_MUL':
        _b = _stack.pop(); _a = _stack.pop()
        _stack.append(_a * _b)
    elif _op == 'V_DIV':
        _b = _stack.pop(); _a = _stack.pop()
        _stack.append(_a / _b)
"""
        payload_b64 = base64.b64encode(payload_script.encode()).decode()
        
        protected_stub = f"""
import sys, os, time, zlib, hashlib, base64

def _vmp():
    _h = []
    _s = (os.getpid() ^ {initial_entropy}) & 0xFFFFFFFF
    _m = {self._generate_mutating_map(initial_entropy, payload_b64, k_n, k_b)}
    
    _addr = {{
        0xEXEC: exec,
        0xCOMP: compile,
        0xHASH: hashlib.sha256
    }}
    
    _ptr = {self._hash_id("ENTRY")}
    _vs = {{'s': 0, 'c': _s}}

    while _ptr:
        if _ptr not in _m: break
        _curr = _m.pop(_ptr)
        _vs['s'] += 1
        _t1 = time.perf_counter_ns()
        try:
            _rl = _addr[0xHASH](str(_h).encode()).digest()
            _sd = _vs['c'] ^ int.from_bytes(_rl[:4], 'big')
            
            _r = list(range(256))
            import random as _rnd; _rnd.seed(_sd); _rnd.shuffle(_r)
            _inv = {{v: k for k, v in enumerate(_r)}}
            
            _dec = bytearray()
            for _b in zlib.decompress(_curr):
                _v = _inv[_b]
                _dec.append(((_v << 1) & 0xFF) | (_v >> 7))
            
            _p_ns = {{'__builtins__': __builtins__}}
            _addr[0xEXEC](_addr[0xCOMP](bytes(_dec), '', 'exec'), _p_ns)
            
            _ptr = _p_ns.get({k_n})
            _bm = _p_ns.get({k_b}, 0)
            _h.append(_ptr)
            _vs['c'] = (_vs['c'] ^ _bm ^ (time.perf_counter_ns() - _t1)) & 0xFFFFFFFF
            _p_ns.clear()
        except Exception:
            _ptr = {self._hash_id("POISON")}
            
    if _vs['s'] > 2:
        os.environ['VMP_AUTH'] = str(_vs['c'])

if __name__ == "__main__":
    _vmp()
"""
        return protected_stub

    def _hash_id(self, name):
        return int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)

    def _generate_mutating_map(self, key, payload_b64, k_n, k_b):
        core_logic = f"import base64; exec(base64.b64decode('{payload_b64}')); "
        blocks = {
            "ENTRY": f"{k_n} = {self._hash_id('CORE')}; {k_b} = 0x1337",
            "CORE": f"{core_logic}{k_n} = {self._hash_id('EXIT')}; {k_b} = 0xDEAD",
            "EXIT": f"{k_n} = None; {k_b} = 0",
            "POISON": "import time; [time.sleep(0.1) for _ in range(10)]"
        }
        m = {}
        curr_c = key
        h_sim = []
        for name in ["ENTRY", "CORE", "EXIT", "POISON"]:
            rolling = hashlib.sha256(str(h_sim).encode()).digest()
            seed = curr_c ^ int.from_bytes(rolling[:4], 'big')
            r = list(range(256)); random.seed(seed); random.shuffle(r)
            comp = zlib.compress(blocks[name].encode())
            trans = bytearray()
            for b in comp:
                rotated = ((b >> 1) | (b << 7)) & 0xFF
                trans.append(r[rotated])
            m[self._hash_id(name)] = bytes(trans)
            h_sim.append(self._hash_id(name))
            if name == "ENTRY": curr_c ^= 0x1337
            elif name == "CORE": curr_c ^= 0xDEAD
        return m

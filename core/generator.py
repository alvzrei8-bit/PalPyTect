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
        payload_script = f"""
import sys
_bc = {self.bc}
_cn = {self.cn}
_stack = []
for _op, _arg in _bc:
    if _op == 'V_LDC':
        _stack.append(_cn[_arg])
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
    _hist = [] 
    _s = (os.getpid() ^ {initial_entropy}) & 0xFFFFFFFF
    _m = {self._generate_mutating_map(initial_entropy, payload_b64)}
    _k_next = sum([ord(x) for x in "NEXT_NODE"]) % 255 
    _k_bump = sum([ord(x) for x in "STATE_BUMP"]) % 255
    _ptr = {self._hash_id("ENTRY")}
    _vm_state = {{'s': 0, 'c': _s}}

    while _ptr:
        if _ptr not in _m: break
        _curr = _m.pop(_ptr)
        _vm_state['s'] += 1
        _t1 = time.perf_counter_ns()
        try:
            _rolling = hashlib.sha256(str(_hist).encode()).digest()
            _seed = _vm_state['c'] ^ int.from_bytes(_rolling[:4], 'big')
            _r = list(range(256)); import random as _rnd; _rnd.seed(_seed); _rnd.shuffle(_r)
            _inv = {{v: k for k, v in enumerate(_r)}}
            _raw = bytearray()
            for _b in zlib.decompress(_curr):
                _v = _inv[_b]
                _raw.append(((_v << 1) & 0xFF) | (_v >> 7))
            _co = compile(bytes(_raw), '', 'exec')
            _raw = None
            _pay_ns = {{}}
            exec(_co, _pay_ns)
            _ptr = _pay_ns.get(_k_next)
            _bump = _pay_ns.get(_k_bump, 0)
            _hist.append(_ptr)
            _vm_state['c'] = (_vm_state['c'] ^ _bump ^ (time.perf_counter_ns() - _t1)) & 0xFFFFFFFF
            _pay_ns.clear()
        except:
            _ptr = {self._hash_id("POISON")}
    if _vm_state['s'] > 2:
        os.environ['VMP_AUTH'] = str(_vm_state['c'])

if __name__ == "__main__":
    _vmp()
"""
        return protected_stub

    def _hash_id(self, name):
        return int(hashlib.sha256(name.encode()).hexdigest()[:12], 16)

    def _generate_mutating_map(self, key, payload_b64):
        core_logic = f"import base64; exec(base64.b64decode('{payload_b64}')); "
        blocks = {
            "ENTRY": "self[210] = " + str(self._hash_id("CORE")) + "; self[222] = 0x1337",
            "CORE": core_logic + "self[210] = " + str(self._hash_id("EXIT")) + "; self[222] = 0xDEAD",
            "EXIT": "self[210] = None; self[222] = 0",
            "POISON": "import time; [time.sleep(0.1) for _ in range(10)]"
        }
        m = {}
        curr_c = key
        history_sim = []
        for name in ["ENTRY", "CORE", "EXIT", "POISON"]:
            rolling = hashlib.sha256(str(history_sim).encode()).digest()
            seed = curr_c ^ int.from_bytes(rolling[:4], 'big')
            r = list(range(256)); random.seed(seed); random.shuffle(r)
            comp = zlib.compress(blocks[name].encode())
            trans = bytearray()
            for b in comp:
                rotated = ((b >> 1) | (b << 7)) & 0xFF
                trans.append(r[rotated])
            m[self._hash_id(name)] = bytes(trans)
            history_sim.append(self._hash_id(name))
            if name == "ENTRY": curr_c ^= 0x1337
            elif name == "CORE": curr_c ^= 0xDEAD
        return m

import random
import zlib
import os
import time
import hashlib

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts

    def generate_stub(self):
        v_key = random.randint(1, 2**32)
        
        protected_stub = f"""
import sys, os, time, zlib

def _vmp_final():
    _s = (os.getpid() ^ int(time.perf_counter() * 1000)) & 0xFFFFFFFF
    _m = {self._generate_opaque_map(v_key)}
    _p = {self._hash_id("ENTRY")}
    _vm_state = {{'steps': 0, 'chain': _s}}
    _target = {len(self._get_blocks()) - 1}

    while _p:
        if _p not in _m: break
        _curr = _m.pop(_p)
        _vm_state['steps'] += 1
        
        try:
            _seed = _vm_state['chain']
            _r = list(range(256))
            import random as _rnd; _rnd.seed(_seed); _rnd.shuffle(_r)
            _inv = {{v: k for k, v in enumerate(_r)}}
            
            _raw = bytearray()
            for _b in zlib.decompress(_curr):
                _v = _inv[_b]
                _raw.append(((_v << 1) & 0xFF) | (_v >> 7))
            
            
            _co = compile(bytes(_raw), '', 'exec')
            _pay_ns = {{}} 
            exec(_co, _pay_ns)
            
            
            if 170 not in _pay_ns: raise Exception()
            
            
            _p = _pay_ns[170]
            _vm_state['chain'] = (_vm_state['chain'] ^ _pay_ns.get(187, 0)) & 0xFFFFFFFF
            
            _pay_ns.clear()
        except:
            
            _p = {self._hash_id("TRAP")}
            _vm_state['chain'] = (_vm_state['chain'] >> 2)

    if _vm_state['steps'] >= _target:
        pass

if __name__ == "__main__":
    _vmp_final()
"""
        return protected_stub

    def _hash_id(self, name):
        return int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)

    def _get_blocks(self):
        return {
            "ENTRY": f"self[170] = {self._hash_id('LOGIC')}; self[187] = 0xDEADC0DE",
            "LOGIC": f"self[170] = {self._hash_id('END')}; self[187] = 0xCAFEBABE",
            "END": "self[170] = None; self[187] = 0",
            "TRAP": "time.sleep(random.random()); [os.getpid() for _ in range(1000)]"
        }

    def _generate_opaque_map(self, key):
        blocks = self._get_blocks()
        opaque_map = {}
        curr_chain = key & 0xFFFFFFFF
        
        for name in ["ENTRY", "LOGIC", "END", "TRAP"]:
            code = blocks[name]
            seed = curr_chain
            
            r = list(range(256))
            random.seed(seed)
            random.shuffle(r)
            
            compressed = zlib.compress(code.encode())
            transformed = bytearray()
            for b in compressed:
                rotated = ((b >> 1) | (b << 7)) & 0xFF
                transformed.append(r[rotated])
            
            opaque_map[self._hash_id(name)] = bytes(transformed)
            
            
            if name == "ENTRY": curr_chain ^= 0xDEADC0DE
            elif name == "LOGIC": curr_chain ^= 0xCAFEBABE
            
        return opaque_map

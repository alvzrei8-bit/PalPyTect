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
        v_key = random.randint(1, 255)
        # Solution 8: Opaque control signals (Hashed/Numeric)
        # 0xAA = Next Node, 0xBB = Key Bump, 0xCC = Step Count
        
        protected_stub = f"""
import sys, os, time, zlib

def _vmp_elite():
    _s = (os.getpid() ^ int(time.perf_counter() * 1000)) % 256
    _m = {self._generate_elite_map(v_key)}
    _ptr = "0xSTART" 
    _ns = {{'_steps': 0}} 
    
    
    _target_steps = 3 

    while _ptr:
        if _ptr not in _m: break
        
        _curr = _m.pop(_ptr) 
        try:
            
            _r = list(range(256))
            import random as _rnd; _rnd.seed(_s); _rnd.shuffle(_r)
            _inv = {{v: k for k, v in enumerate(_r)}}
            _raw = bytearray()
            for _b in zlib.decompress(_curr):
                _v = _inv[_b]
                _raw.append(((_v << 1) & 0xFF) | (_v >> 7))
            
            
            _code_obj = compile(bytes(_raw), '<vmp>', 'exec')
            exec(_code_obj, _ns)
            
            
            if 0xAA not in _ns: raise RuntimeError("ABI_VIOLATION")
            
            _ptr = _ns[0xAA] 
            _s = (_s + _ns.get(0xBB, 0)) % 256 # Opaque 'bump'
            
            
            _keep = {{0xAA, 0xBB, '_steps'}}
            _ns = {{k: v for k, v in _ns.items() if k in _keep}}
            
        except Exception:
            _s = (_s * 13) % 256
            _ptr = "0xTRAP"

    
    if _ns.get('_steps') != _target_steps:
        pass 

if __name__ == "__main__":
    _vmp_elite()
"""
        return protected_stub

    def _generate_elite_map(self, key):
        """Implements the Formal ABI and Opaque Signals."""
        # 0xAA = next node name, 0xBB = key bump
        blocks = {
            "0xSTART": "self[0xAA] = '0xLOGIC'; self[0xBB] = 17; self['_steps'] += 1",
            "0xLOGIC": "print('Proof of Execution'); self[0xAA] = '0xEND'; self[0xBB] = 5; self['_steps'] += 1",
            "0xEND": "self[0xAA] = None; self['_steps'] += 1",
            "0xTRAP": "time.sleep(5); sys.exit()"
        }
        
        elite_map = {}
        curr_key = key
        
        # Note: 'self' in the block refers to the _ns dictionary
        for node, code in blocks.items():
            # Encrypt
            sub_map = list(range(256))
            random.seed(curr_key)
            random.shuffle(sub_map)
            
            # Transform: Bit rotate then substitute
            compressed = zlib.compress(code.encode())
            transformed = bytearray()
            for b in compressed:
                rotated = ((b >> 1) | (b << 7)) & 0xFF
                transformed.append(sub_map[rotated])
            
            elite_map[node] = bytes(transformed)
            
            # Key evolution
            if node == "0xSTART": curr_key = (curr_key + 17) % 256
            elif node == "0xLOGIC": curr_key = (curr_key + 5) % 256
            
        return elite_map

import random
import zlib
import base64
from core.obfuscation import Obfuscator
from core.predicates import PredicateFactory

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.ob = Obfuscator()

    def _elite_transform(self, data, key, reverse=False):
        """Solution 6: Multi-layer transform (Rotate + Substitution)."""
        output = bytearray()
        # Create a substitution map based on the key
        sub_map = list(range(256))
        random.seed(key)
        random.shuffle(sub_map)
        
        if reverse:
            inv_map = {v: k for k, v in enumerate(sub_map)}
            for b in data:
                # Reverse substitution then bit-rotation
                val = inv_map[b]
                output.append(((val << 1) & 0xFF) | (val >> 7))
        else:
            for b in data:
                # Bit-rotation then substitution
                rotated = ((b >> 1) | (b << 7)) & 0xFF
                output.append(sub_map[rotated])
        return bytes(output)

    def generate_stub(self):
        v_key = random.randint(1, 255)
        # Solutions 8 & 11: Indirect lookups for control variables
        node_var = self.ob.dna_id(8)
        key_var = self.ob.dna_id(8)
        
        # Solution 3: Enforce entry node
        protected_stub = f"""
import sys, os, time, zlib

def _vmp():
    _s = (os.getpid() ^ int(time.perf_counter() * 1000)) % 256
    _m = {self._generate_state_map(v_key)}
    _n = "start" # Mandatory Entry Node
    _ns = {{}}

    while _n in _m:
        _ns['_key_gate'] = _s
        _curr = _m.pop(_n)
        
        try:
            _seed = _s
            _sub = list(range(256))
            import random as _r; _r.seed(_seed); _r.shuffle(_sub)
            _inv = {{v: k for k, v in enumerate(_sub)}}
            _d = bytearray()
            for _b in zlib.decompress(_curr):
                _v = _inv[_b]
                _d.append(((_v << 1) & 0xFF) | (_v >> 7))
            
            exec(bytes(_d), _ns)
            _n = _ns.get('_next', 'trap')
            _s = (_s + _ns.get('_bump', 0)) % 256
            
            
            _d = None 
        except Exception:
           
            _n = "trap"
            _s = (_s * 7) % 256


if __name__ == "__main__":
    _vmp()
"""
        return protected_stub

    def _generate_state_map(self, key):
        """Upgrade 1 & 3: Mandatory ABI and Node Mapping."""
        # Note: In a real build, these blocks contain your actual VM logic
        blocks = {
            "start": "import os; _next = 'logic_01'; _bump = 13",
            "logic_01": "def main(): pass; _next = 'exit'; _bump = 21",
            "exit": "import sys; _next = None",
            "trap": "time.sleep(10); os._exit(1)"
        }
        
        state_map = {}
        curr_key = key
        for node, code in blocks.items():
            # Apply the elite transform
            transformed = self._elite_transform(zlib.compress(code.encode()), curr_key)
            state_map[node] = transformed
            # Predict the key evolution to match the runtime _bump
            if node == "start": curr_key = (curr_key + 13) % 256
            elif node == "logic_01": curr_key = (curr_key + 21) % 256
            
        return state_map

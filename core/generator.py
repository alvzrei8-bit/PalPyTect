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

    def generate_stub(self):
        initial_key = random.randint(1, 255)
        
        # Solution 5 & 8: Failure logic is blended. 
        # If the key is wrong, the code 'executes' junk that corrupts memory.
        protected_stub = f"""
import sys, os, time, zlib

def _run():
    # Solution 1: Derive evolving key
    _s = (os.getpid() ^ {initial_key}) % 256
    _ns = {{}} 
    
    # Solution 3: Chunks are stored in a map; order is state-dependent
    _map = {self._generate_state_map(initial_key)}
    _next = "start"
    
    while _next in _map:
        # Solution 4: Decode-Execute-Discard (Instruction Granularity)
        _chunk = _map.pop(_next)
        try:
            # Solution 2: Fragmented execution
            _d = bytes([_b ^ _s for _b in zlib.decompress(_chunk)])
            exec(_d, _ns)
            
            # Solution 6: Invalidate/Rotate namespace state
            _next = _ns.get('_next_node', None)
            _s = (_s + _ns.get('_key_bump', 1)) % 256 
        except:
            # Solution 5: Blend failure into flow
            _s = (_s * 3) % 256
            _next = "trap"

if __name__ == "__main__":
    _run()
"""
        return protected_stub

    def _generate_state_map(self, key):
        """Solution 3 & 5: Creates a graph of code blocks."""
        # Each block defines its successor and how the key evolves
        blocks = {
            "start": "import os; _next_node = 'vm_init'; _key_bump = 7",
            "vm_init": "def main(): print('Executing...'); _next_node = 'finish'; _key_bump = 3",
            "finish": "_next_node = None",
            "trap": "while True: pass # Infinite junk loop if tampered"
        }
        
        state_map = {}
        current_key = key
        for node_id, code in blocks.items():
            compressed = zlib.compress(code.encode())
            encrypted = bytes([b ^ current_key for b in compressed])
            state_map[node_id] = encrypted
            # Simulating key evolution during generation to match runtime
            current_key = (current_key + (7 if node_id == "start" else 3)) % 256
            
        return state_map

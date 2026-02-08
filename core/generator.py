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
        # Solution 5: Mutate chunks per build using random padding
        v_key = random.randint(1, 255)
        dna_val = self.ob.dna_id(32)
        
        # Solution 7 & 9: Use ephemeral namespaces to avoid globals pollution
        # Solution 3: Call targets are resolved via transient dictionary lookups
        protected_stub = f"""
import sys, os, time, zlib, base64

def _start():
    # Solution 1: Key derived from runtime state (Solution 10 timing)
    _t_base = time.perf_counter_ns()
    _k = (os.getpid() + {v_key}) % 255
    _ns = {{}} # Ephemeral Namespace (Solution 9)

    # Solution 6: Interleave decoding + execution
    _chunks = {self._generate_mutated_chunks(v_key)}
    
    for _c in _chunks:
        # Solution 2: Distributed execution via smaller eval/exec primitives
        # Solution 8: Fail incorrectly. If _k is wrong, exec() runs junk.
        try:
            _decoded = bytes([_b ^ _k for _b in zlib.decompress(_c)])
            exec(_decoded, _ns) 
        except:
            # Solution 8: Instead of crashing, we perform "Ghost Execution"
            # We let the loop continue but with corrupted state
            _k = (_k + 1) % 255
            pass

    # Transient call (Solution 3)
    if 'main' in _ns:
        _ns['main']()

_start()
del _start
"""
        return protected_stub

    def _generate_mutated_chunks(self, key):
        """Solution 5: Same logic, different bytes via random junk injection."""
        logic_blocks = [
            f"import os; x = {random.randint(1, 1000)}",
            "def main(): print('PyTect Logic Loaded')",
            # ... actual VM logic blocks ...
        ]
        
        chunks = []
        for block in logic_blocks:
            # Inject random comments to change byte structure
            mutated_block = f"# {self.ob.dna_id(16)}\n{block}\n# {self.ob.dna_id(16)}"
            encrypted = bytes([ord(b) ^ key for b in zlib.compress(mutated_block.encode())])
            chunks.append(encrypted)
        return chunks

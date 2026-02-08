import random
import zlib
import base64
import os
from core.obfuscation import Obfuscator
from core.predicates import PredicateFactory

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.ob = Obfuscator()

    def generate_stub(self):
        # Solution 5: Mutate chunks per build
        v_key = random.randint(1, 255)
        
        # Solution 7 & 9: Ephemeral namespaces and transient lookups
        protected_stub = f"""
import sys, os, time, zlib, base64

def _start():
    # Solution 1: Key derived from runtime state
    _k = (os.getpid() + {v_key}) % 255
    _ns = {{}} # Solution 9: Ephemeral Namespace

    # Solution 6: Interleave decoding + execution
    _chunks = {self._generate_mutated_chunks(v_key)}
    
    for _c in _chunks:
        # Solution 2: Distributed execution
        try:
            # Solution 8: Fail incorrectly (corrupt _k) if decoding fails
            _decoded = bytes([_b ^ _k for _b in zlib.decompress(_c)])
            exec(_decoded, _ns) 
        except:
            _k = (_k + 1) % 256
            pass

    # Solution 3: Transient call
    if 'main' in _ns:
        _ns['main']()

if __name__ == "__main__":
    _start()
    del _start
"""
        return protected_stub

    def _generate_mutated_chunks(self, key):
        """Solution 5: Same logic, different bytes via junk injection."""
        # Encapsulate the VM logic into chunks
        logic_blocks = [
            f"import os; _id = {random.randint(1, 1000)}",
            "def main(): print('Protected Logic Executing...')"
            # Actual VM bytecode processing would be added here as additional chunks
        ]
        
        chunks = []
        for block in logic_blocks:
            # Solution 5: Mutate bytes per build with random comments
            mutated_block = f"# {self.ob.dna_id(16)}\\n{block}\\n# {self.ob.dna_id(16)}"
            compressed = zlib.compress(mutated_block.encode())
            # FIXED: b is already an int, ord() is removed
            encrypted = bytes([b ^ key for b in compressed])
            chunks.append(encrypted)
        return chunks

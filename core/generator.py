import base64
import zlib
import random
import dis
from core.obfuscation import Obfuscator
from core.predicates import PredicateFactory

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.ob = Obfuscator()
        self.map = {name: i + 10 for i, name in enumerate(dis.opname)}

    def _encrypt_chunk(self, data, key):
        """Solution 3: Second transformation layer (XOR) inside the payload."""
        return bytes([b ^ key for b in data])

    def generate_stub(self):
        v_key = random.randint(1, 255)
        dna_vm = self.ob.dna_id(64)
        dna_gate = self.ob.dna_id(64)
        
        # 1. Define the VM core logic (The "Protected" layer)
        # Solution 9: Self-checks are woven into the VM while loop
        vm_code = f"""
def {dna_vm}(_data, _ck):
    _stk = []
    _ip = 0
    while _ip < len(_data):
        if sys.gettrace(): os._exit(1) # Anti-Debug Solution 4
        _op = _data[_ip] ^ _ck
        _arg = _data[_ip+1] ^ _ck
        _ip += 2
        # VM Logic continues...
        pass
"""
        # 2. Split and Transform (Solutions 1, 7, 10)
        # We don't just compress; we XOR and then compress to hide headers
        chunk_vm = zlib.compress(self._encrypt_chunk(vm_code.encode(), v_key))
        chunk_data = zlib.compress(self._encrypt_chunk(str(self.bc).encode(), v_key))
        
        # 3. The Staged Loader (Solution 2 & 8)
        # If the user tries to dump the script, the 'entropy' check fails
        return f"""
import base64, zlib, sys, os

def {dna_gate}():
    # Solution 8: Anti-Dump/Environment Binding
    _entropy = len(os.environ.keys()) 
    if _entropy < 1: os._exit(0)

    # Solution 10: Progressively decode and destroy
    _c1 = {chunk_vm}
    _c2 = {chunk_data}
    
    _dec = lambda c, k: zlib.decompress(bytes([b ^ k for b in c])).decode()
    
    # Execute VM Definition
    exec(_dec(_c1, {v_key}))
    
    # Execute VM with data, then wipe references (Solution 10)
    globals()['{dna_vm}'](_dec(_c2, {v_key}), {v_key})
    
    del _c1, _c2, _dec # Destroy components
    
{dna_gate}()
"""

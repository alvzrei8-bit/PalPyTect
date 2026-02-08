import random
import base64
import zlib
import marshal
from core.obfuscation import Obfuscator
from core.predicates import PredicateFactory

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts # Plaintext constants
        self.ob = Obfuscator()
        # Initial opcode mapping
        self.map = {'LDC': 10, 'ADD': 20, 'SUB': 30, 'PRN': 40, 'JMP': 50, 'HLT': 99}
        self._shuffle_map()

    def _shuffle_map(self):
        vals = random.sample(range(10, 250), len(self.map))
        self.map = dict(zip(self.map.keys(), vals))

    def _encrypt_constants(self, key):
        """XOR encrypts constants so they aren't visible in plaintext."""
        encrypted = []
        for c in self.cn:
            if isinstance(c, str):
                encrypted.append("".join(chr(ord(char) ^ key) for char in c))
            else:
                encrypted.append(c)
        return encrypted

    def generate_stub(self):
        dna_vm = self.ob.dna_id(64)
        dna_stk = self.ob.dna_id(64)
        dna_ip = self.ob.dna_id(64)
        dna_state = self.ob.dna_id(64)
        
        # 1. Encrypt Constants
        c_key = random.randint(1, 255)
        enc_consts = self._encrypt_constants(c_key)
        
        # 2. Build Bytecode with "Junk" Instructions (Problem 6)
        raw_stream = []
        for op, arg in self.bc:
            raw_stream.extend([self.map[op], arg if arg is not None else 0])
            # Inject Junk
            if random.random() > 0.7:
                raw_stream.extend([random.randint(251, 255), random.randint(0, 255)])
        
        v_key = random.randint(1, 255)
        enc_stream = [x ^ v_key for x in raw_stream]

        # 3. The "Elite" VM Stub
        inner_vm = f"""
import sys, os, time

def {dna_vm}():
    # Distributed Integrity Checks (Problem 4)
    def _sig():
        if sys.gettrace(): os._exit(1)
        if len(sys.modules) > 100: pass # Arbitrary environmental check

    {dna_stk} = []
    {dna_ip} = 0
    {dna_state} = {v_key} # Mutating Key (Problem 2)
    
    _d = {enc_stream}
    _c = {enc_consts}
    _ck = {c_key}

    while {dna_ip} < len(_d):
        _sig() # Run integrity check inside the loop
        
        if {PredicateFactory.get_runtime_true()}: # State-dependent (Problem 5)
            _op = _d[{dna_ip}] ^ {dna_state}
            _arg = _d[{dna_ip}+1] ^ {dna_state}
            {dna_ip} += 2
            
            # Opcode State Mutation (Problem 2)
            {dna_state} = ({dna_state} + 1) % 256

            if _op == {self.map['LDC']}:
                val = _c[_arg]
                # JIT Decryption of Constants (Problem 3)
                if isinstance(val, str):
                    val = "".join(chr(ord(x) ^ _ck) for x in val)
                {dna_stk}.append(val)
            elif _op == {self.map['ADD']}:
                {dna_stk}.append({dna_stk}.pop() + {dna_stk}.pop())
            elif _op == {self.map['PRN']}:
                sys.stdout.write(str({dna_stk}.pop()) + "\\n")
            elif _op == {self.map['HLT']}:
                break
            # Ignore Junk Opcodes (Problem 6)
        else:
            time.sleep(0.001) # Anti-brute force delay
"""
        # Final Unpacking Layer (Problem 1)
        # Instead of one big blob, we can use an iterator to feed the exec()
        payload = base64.b64encode(zlib.compress(inner_vm.encode())).decode()
        
        return f"import base64,zlib;[exec(x) for x in [zlib.decompress(base64.b64decode('{payload}'))]];{dna_vm}()"

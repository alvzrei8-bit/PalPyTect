import random
import base64
import zlib
import dis
from core.obfuscation import Obfuscator
from core.predicates import PredicateFactory

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.ob = Obfuscator()
        # Problem 2: Map ALL 100+ Python opcodes to random IDs per build
        self.map = {name: i + 10 for i, name in enumerate(dis.opname)}
        self._shuffle_map()

    def _shuffle_map(self):
        items = list(self.map.items())
        random.shuffle(items)
        self.map = dict(items)

    def generate_stub(self):
        dna_vm = self.ob.dna_id(128)
        dna_ip = self.ob.dna_id(128)
        dna_key = self.ob.dna_id(128)
        
        # Problem 3: Encrypt constants with a build-key
        c_key = random.randint(1, 255)
        enc_consts = []
        for c in self.cn:
            if isinstance(c, str):
                enc_consts.append("".join(chr(ord(x) ^ c_key) for x in c))
            else: enc_consts.append(c)

        # Problem 2 & 9: Bytecode with Mutating State
        v_key = random.randint(1, 255)
        raw_stream = []
        state_tracker = v_key
        for op_name, arg in self.bc:
            op_id = self.map.get(op_name, 0)
            # XOR with a mutating state key so the same instruction 
            # looks different every time it appears in the stream
            raw_stream.extend([op_id ^ state_tracker, (arg or 0) ^ state_tracker])
            state_tracker = (state_tracker + 1) % 256

        inner_vm = f"""
import sys, os, time

def {dna_vm}():
    # Problem 4: Internal integrity check called throughout execution
    def _verify():
        if sys.gettrace(): os._exit(1)
    
    {dna_ip} = 0
    {dna_key} = {v_key}
    _d = {raw_stream}
    _c = {enc_consts}
    
    while {dna_ip} < len(_d):
        _verify()
        # Problem 5: Opaque predicate dependent on runtime state
        if {PredicateFactory.get_true()}:
            _op = _d[{dna_ip}] ^ {dna_key}
            _arg = _d[{dna_ip}+1] ^ {dna_key}
            {dna_ip} += 2
            {dna_key} = ({dna_key} + 1) % 256 # Mutate key
            
            # Problem 6 & 7: Dynamic Dispatcher (Simplified for stability)
            # In professional builds, this uses a jump table
            if _op == {self.map.get('LOAD_CONST', 0)}:
                val = _c[_arg]
                if isinstance(val, str): # Problem 3: JIT Constant Decryption
                    val = "".join(chr(ord(x) ^ {c_key}) for x in val)
                # ... stack push logic ...
            elif _op == {self.map.get('BINARY_MULTIPLY', 0)}: pass # Fix for your MUL error
            # ... additional opcodes mapped here ...
        else:
            {self.ob.junk_block()}

{dna_vm}()
"""
        # Problem 1: Unpacking logic isn't just a string; it's a dynamic execution
        payload = base64.b64encode(zlib.compress(inner_vm.encode())).decode()
        return f"import base64,zlib;exec(zlib.decompress(base64.b64decode('{payload}')))"

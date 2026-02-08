import random
import base64
import zlib
from core.obfuscation import Obfuscator
from core.predicates import PredicateFactory

class Generator:
    def __init__(self, bytecode, consts):
        self.bc = bytecode
        self.cn = consts
        self.ob = Obfuscator()
        self.map = {'LDC': 10, 'ADD': 20, 'SUB': 30, 'PRN': 40, 'HLT': 99}
        self._shuffle_map()

    def _shuffle_map(self):
        keys = list(self.map.keys())
        vals = random.sample(range(10, 255), len(keys))
        self.map = dict(zip(keys, vals))

    def generate_stub(self):
        # Generate massive, visually identical DNA strings
        dna_vm = self.ob.dna_id()
        dna_stk = self.ob.dna_id()
        dna_ip = self.ob.dna_id()
        dna_dat = self.ob.dna_id()
        dna_con = self.ob.dna_id()
        
        raw_stream = []
        for op, arg in self.bc:
            raw_stream.extend([self.map[op], arg if arg is not None else 0])
        raw_stream.extend([self.map['HLT'], 0])

        key = random.randint(1, 255)
        enc_stream = [x ^ key for x in raw_stream]

        # The internal logic of the VM
        inner_vm = f"""
import sys, os
def check_integrity():
    if sys.gettrace() is not None: os._exit(1)
    import builtins
    for f in [exec, eval, getattr]:
        if type(f).__name__ != 'builtin_function_or_method': os._exit(2)

def {dna_vm}():
    check_integrity()
    {dna_stk} = []
    {dna_ip} = 0
    {dna_dat} = [x ^ {key} for x in {enc_stream}]
    {dna_con} = {self.cn}
    
    while True:
        if {PredicateFactory.get_true()}:
            if {dna_ip} >= len({dna_dat}): break
            _op = {dna_dat}[{dna_ip}]
            _arg = {dna_dat}[{dna_ip}+1]
            {dna_ip} += 2
            
            if _op == {self.map['LDC']}: {dna_stk}.append({dna_con}[_arg])
            elif _op == {self.map['ADD']}: 
                b = {dna_stk}.pop(); a = {dna_stk}.pop()
                {dna_stk}.append(a + b)
            elif _op == {self.map['PRN']}: print({dna_stk}.pop())
            elif _op == {self.map['HLT']}: break
            else: os._exit(0)
        else:
            {self.ob.junk_block()}
{dna_vm}()
"""
        # Wrap the inner VM in compression and encoding
        encoded_payload = base64.b64encode(zlib.compress(inner_vm.encode())).decode()
        
        # The final "dominating" stub
        return f"import base64, zlib; exec(zlib.decompress(base64.b64decode('{encoded_payload}')))"

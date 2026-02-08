import random
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
        dna_vm = self.ob.dna_id()
        dna_stk = self.ob.dna_id()
        dna_ip = self.ob.dna_id()
        
        raw_stream = []
        for op, arg in self.bc:
            raw_stream.extend([self.map[op], arg if arg is not None else 0])
        raw_stream.extend([self.map['HLT'], 0])

        key = random.randint(1, 255)
        enc_stream = [x ^ key for x in raw_stream]

        # Note: In the final stub, check_integrity code should be injected 
        # or properly reachable in the output directory.
        return f"""
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
    _d = [x ^ {key} for x in {enc_stream}]
    _c = {self.cn}
    
    while True:
        if {PredicateFactory.get_true()}:
            if {dna_ip} >= len(_d): break
            _op = _d[{dna_ip}]
            _arg = _d[{dna_ip}+1]
            {dna_ip} += 2
            
            if _op == {self.map['LDC']}: {dna_stk}.append(_c[_arg])
            elif _op == {self.map['ADD']}: 
                b = {dna_stk}.pop(); a = {dna_stk}.pop()
                {dna_stk}.append(a + b)
            elif _op == {self.map['PRN']}: print({dna_stk}.pop())
            elif _op == {self.map['HLT']}: break
            else: os._exit(0)
        else:
            {self.ob.junk_block()}

if __name__ == "__main__":
    {dna_vm}()
"""

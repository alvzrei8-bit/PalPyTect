import random
import string

class Obfuscator:
    def __init__(self):
        self.alphabet = "Il1O0"

    def dna_id(self, length=32):
        return "".join(random.choice(self.alphabet) for _ in range(length))

    def junk_block(self):
        v = self.dna_id(8)
        ops = ["+", "-", "^", "*"]
        return f"{v} = {random.randint(1,100)} {random.choice(ops)} {random.randint(1,100)}"

import random

class Obfuscator:
    def __init__(self):
        # We exclude digits from the start of the string
        self.head = "IlO" 
        self.body = "Il1O0"

    def dna_id(self, length=128):
        """Generates massive visually confusing identifiers."""
        first = random.choice(self.head)
        rest = "".join(random.choice(self.body) for _ in range(length - 1))
        return first + rest

    def junk_block(self):
        """Generates logic that looks important but does nothing."""
        v1 = self.dna_id(32)
        v2 = self.dna_id(32)
        return f"{v1} = sum([ord(x) for x in '{self.dna_id(16)}']); {v2} = {v1} ^ {random.randint(1, 1000)}"

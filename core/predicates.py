import random
import os
import sys

class PredicateFactory:
    @staticmethod
    def get_runtime_true():
        """Solution 4 & 10: Logic bound to runtime environment signals."""
        n = random.randint(1, 100)
        p_list = [
            f"(os.getpid() > 0)", 
            f"(sum(range({n})) == {sum(range(n))})",
            f"(len(os.environ.keys()) > 0)",
            f"(sys.flags.optimize == {sys.flags.optimize})"
        ]
        return random.choice(p_list)

    @staticmethod
    def get_complex_false():
        return "(lambda x: x == x + 1)(random.random())"

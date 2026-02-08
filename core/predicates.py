import random
import time
import os

class PredicateFactory:
    @staticmethod
    def get_runtime_true():
        """Predicates that depend on the environment or process state."""
        n = random.randint(1, 100)
        # These are always true but require runtime execution to verify
        p_list = [
            f"(os.getpid() > 0)", 
            f"(sum(range({n})) == {sum(range(n))})",
            f"(len(sys.argv) >= 0)",
            f"(type(None) is not type(int))"
        ]
        return random.choice(p_list)

    @staticmethod
    def get_complex_false():
        """Contradictions that look like complex logic."""
        return "(lambda x: x == x + 1)(random.random())"

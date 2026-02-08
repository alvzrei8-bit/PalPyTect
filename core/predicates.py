import random
import time
import os

class PredicateFactory:
    @staticmethod
    def get_true():
        """Returns math tautologies that always evaluate to True."""
        n = random.randint(1, 1000)
        p_list = [
            f"((7*({n}**2) + 1) % 3 != 0)",
            f"(({n} * ({n} + 1)) % 2 == 0)",
            f"(pow({n}, 2, 4) != 2)",
            f"(os.getpid() > 0)"
        ]
        return random.choice(p_list)

    @staticmethod
    def get_runtime_true():
        """Predicates that depend on the environment or process state."""
        n = random.randint(1, 100)
        p_list = [
            f"(sum(range({n})) == {sum(range(n))})",
            f"(len(sys.argv) >= 0)",
            f"(type(None) is not type(int))"
        ]
        return random.choice(p_list)

    @staticmethod
    def get_complex_false():
        """Contradictions that look like complex logic."""
        return "(lambda x: x == x + 1)(random.random())"

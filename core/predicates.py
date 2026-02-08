import random
import os
import sys

class PredicateFactory:
    @staticmethod
    def get_runtime_state_check():
        """Solution 4 & 6: Binds logic to non-deterministic runtime values."""
        n = random.randint(1, 100)
        # These checks are designed to fail in a debugger or sandbox
        states = [
            f"(os.getppid() > 1)", 
            f"(len(os.environ.keys()) > 5)",
            f"(sys.flags.optimize == {sys.flags.optimize})",
            f"(sum(range({n})) == {sum(range(n))})"
        ]
        return random.choice(states)

    @staticmethod
    def get_true():
        return f"({PredicateFactory.get_runtime_state_check()})"

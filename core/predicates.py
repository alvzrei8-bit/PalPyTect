import random

class PredicateFactory:
    @staticmethod
    def get_true():
        """Returns math tautologies: 7n^2 + 1 is never 0 mod 3."""
        n = random.randint(1, 1000)
        p_list = [
            f"((7*({n}**2) + 1) % 3 != 0)",
            f"(({n} * ({n} + 1)) % 2 == 0)",
            f"(pow({n}, 2, 4) != 2)"
        ]
        return random.choice(p_list)

    @staticmethod
    def get_false():
        """Returns contradictions: x^2 + y^2 = 4n+3 is impossible."""
        x, y = random.randint(1, 10), random.randint(1, 10)
        return f"(({x}**2 + {y}**2) % 4 == 3)"

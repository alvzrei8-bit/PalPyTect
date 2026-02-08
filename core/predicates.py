import random
import os
import sys
import time

class PredicateFactory:
    @staticmethod
    def get_runtime_entropy():
        t = time.perf_counter_ns()
        return (os.getpid() ^ (t % 1000)) % 256

    @staticmethod
    def get_true():
        n = random.randint(1, 1000)
        return f"({n}*{n} >= 0)"

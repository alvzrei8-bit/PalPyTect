import time
import os
import sys
import platform

class PredicateFactory:
    @staticmethod
    def get_runtime_entropy():
        """Solution 4 & 10: Aggregates weak signals from the platform and timing."""
        # Non-Python dependency: timing jitter + platform specific quirks
        t1 = time.perf_counter_ns()
        _ = [os.getpid() for _ in range(10)]
        t2 = time.perf_counter_ns()
        
        # Combine signals: PID, Platform string length, and execution jitter
        sig = os.getpid() + len(platform.platform()) + (t2 - t1)
        return sig % 255

    @staticmethod
    def get_opaque_predicate():
        """Solution 8: Instead of crashing, we return a value that causes incorrect logic."""
        # If a debugger is found, instead of exit(), we return a value that 
        # makes the XOR key wrong later, causing the VM to run 'ghost' instructions.
        if sys.gettrace() is not None:
            return "66" # The 'False' signal that corrupts state
        return "0"

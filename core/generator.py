import zlib
import time
import os

class Generator:
    def __init__(self, source):
        self.src = source

    def generate_stub(self):
        entropy = int(time.perf_counter() * 1000) & 0xFFFFFFFF
        payload = zlib.compress(self.src.encode())

        return f'''
import zlib, os, time

def _run():
    _data = {payload!r}
    _code = zlib.decompress(_data)
    exec(_code, {{'__name__': '__main__'}})

if __name__ == "__main__":
    _run()
'''

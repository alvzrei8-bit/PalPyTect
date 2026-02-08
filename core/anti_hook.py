import sys
import os

def check_integrity():
    # Detect Debugger
    if sys.gettrace() is not None:
        os._exit(1)
    
    # Detect Hooking of critical built-ins
    import builtins
    for f in [exec, eval, getattr]:
        if type(f).__name__ != 'builtin_function_or_method':
            os._exit(2)
            
    # Detect Instrumentation Frameworks (Frida/etc)
    if 'frida' in sys.modules or 'pydbg' in sys.modules:
        os._exit(3)
      

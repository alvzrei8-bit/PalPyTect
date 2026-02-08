class NestedVM:
    """
    Layer 2 (L2) VM logic. 
    L1 VM Instructions: [EXEC_L2, <L2_Bytecode_Pointer>]
    """
    def __init__(self, constants):
        self.constants = constants

    def execute_layer(self, l2_stream):
        # L2-specific registers
        _r1 = 0
        _r2 = 0
        _ip = 0
        
        while _ip < len(l2_stream):
            op = l2_stream[_ip]
            arg = l2_stream[_ip+1]
            _ip += 2
            
            # Simple L2 OpCodes (Harder to trace from L1)
            if op == 0xA1: # LOAD_VAL
                _r1 = self.constants[arg]
            elif op == 0xB2: # OUT
                print(_r1)
            elif op == 0xFF: # HALT
                break

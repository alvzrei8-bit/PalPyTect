import dis

class CustomCompiler:
    def __init__(self):
        self.instructions = []
        self.consts = []

    def compile(self, source):
        code_obj = compile(source, '<string>', 'exec')
        self.consts = list(code_obj.co_consts)
        
        for instr in dis.get_instructions(code_obj):
            # Map every native Python opcode to our Custom VM
            self.instructions.append((instr.opname, instr.arg))
            
        return self.instructions, self.consts

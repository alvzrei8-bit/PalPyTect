import ast

class CustomCompiler(ast.NodeVisitor):
    def __init__(self):
        self.instructions = []
        self.consts = []

    def compile(self, source):
        tree = ast.parse(source)
        self.visit(tree)
        return self.instructions, self.consts

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        # Solutions 2: Operations are fragmented into VM opcodes
        op_map = {
            ast.Add: 'V_ADD', ast.Sub: 'V_SUB', ast.Mult: 'V_MUL',
            ast.Div: 'V_DIV', ast.Mod: 'V_MOD'
        }
        self.instructions.append((op_map.get(type(node.op)), None))

    def visit_Constant(self, node):
        if node.value not in self.consts:
            self.consts.append(node.value)
        self.instructions.append(('V_LDC', self.consts.index(node.value)))

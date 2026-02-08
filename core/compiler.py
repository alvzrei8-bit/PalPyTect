import ast

class CustomCompiler(ast.NodeVisitor):
    def __init__(self):
        self.bytecode = []
        self.consts = []

    def compile(self, source):
        tree = ast.parse(source)
        self.visit(tree)
        return self.bytecode, self.consts

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        # Mapping all arithmetic for the PyTect Progress Bar
        op_map = {
            ast.Add: 'BINARY_ADD', ast.Sub: 'BINARY_SUBTRACT',
            ast.Mult: 'BINARY_MULTIPLY', ast.Div: 'BINARY_TRUE_DIVIDE',
            ast.FloorDiv: 'BINARY_FLOOR_DIVIDE', ast.Mod: 'BINARY_MODULO'
        }
        self.bytecode.append((op_map[type(node.op)], None))
    
    # Standard Constant and Call handlers...
    def visit_Constant(self, node):
        if node.value not in self.consts: self.consts.append(node.value)
        self.bytecode.append(('LOAD_CONST', self.consts.index(node.value)))

    def visit_Call(self, node):
        for arg in node.args: self.visit(arg)
        self.bytecode.append(('CALL_FUNCTION', len(node.args)))

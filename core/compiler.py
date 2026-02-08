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
        op_map = {
            ast.Add: 'OP_ADD', ast.Sub: 'OP_SUB', ast.Mult: 'OP_MUL',
            ast.Div: 'OP_DIV', ast.FloorDiv: 'OP_FDIV', ast.Mod: 'OP_MOD'
        }
        self.instructions.append((op_map.get(type(node.op), 'OP_UNKNOWN'), None))

    def visit_Constant(self, node):
        if node.value not in self.consts:
            self.consts.append(node.value)
        self.instructions.append(('OP_LDC', self.consts.index(node.value)))

    def visit_Call(self, node):
        for arg in node.args: self.visit(arg)
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.instructions.append(('OP_PRN', None))

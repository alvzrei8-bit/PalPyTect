import ast

class CustomCompiler(ast.NodeVisitor):
    def __init__(self):
        self.instructions = []
        self.consts = []

    def compile(self, source):
        self.visit(ast.parse(source))
        return self.instructions, self.consts

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ops = {ast.Add: 'V_ADD', ast.Sub: 'V_SUB', ast.Mult: 'V_MUL', ast.Div: 'V_DIV'}
        self.instructions.append((ops.get(type(node.op), 'V_NOP'), None))

    def visit_Constant(self, node):
        if node.value not in self.consts: self.consts.append(node.value)
        self.instructions.append(('V_LDC', self.consts.index(node.value)))

    def visit_Call(self, node):
        for arg in node.args: self.visit(arg)
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.instructions.append(('V_PRN', None))

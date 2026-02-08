import ast

class CustomCompiler(ast.NodeVisitor):
    def __init__(self):
        self.bytecode = []
        self.consts = []

    def compile(self, source):
        tree = ast.parse(source)
        self.visit(tree)
        return self.bytecode, self.consts

    def visit_Constant(self, node):
        if node.value not in self.consts:
            self.consts.append(node.value)
        self.bytecode.append(('LOAD_CONST', self.consts.index(node.value)))

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        # Added Div and FloorDiv to handle the progress bar logic
        op_map = {
            ast.Add: 'BINARY_ADD', 
            ast.Sub: 'BINARY_SUBTRACT', 
            ast.Mult: 'BINARY_MULTIPLY',
            ast.Div: 'BINARY_TRUE_DIVIDE',
            ast.FloorDiv: 'BINARY_FLOOR_DIVIDE'
        }
        self.bytecode.append((op_map[type(node.op)], None))

    def visit_Call(self, node):
        for arg in node.args: self.visit(arg)
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.bytecode.append(('PRINT_EXPR', None))

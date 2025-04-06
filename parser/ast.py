"""
Abstract Syntax Tree nodes for the Simple Compiler
"""

class AST:
    """Base AST node class"""
    def __init__(self, token=None):
        self.token = token  # For error reporting

    @property
    def position(self):
        if self.token:
            return f"line {self.token.line}, column {self.token.column}"
        return "unknown position"

class BinOp(AST):
    """Binary operation node"""
    def __init__(self, left, op, right):
        super().__init__(op)
        self.left = left
        self.op = op
        self.right = right

class Number(AST):
    """Number literal node"""
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

class String(AST):
    """String literal node"""
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

class UnaryOp(AST):
    """Unary operation node"""
    def __init__(self, op, expr):
        super().__init__(op)
        self.op = op
        self.expr = expr

class Var(AST):
    """Variable reference node"""
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

class Assign(AST):
    """Assignment node"""
    def __init__(self, left, op, right):
        super().__init__(op)
        self.left = left
        self.op = op
        self.right = right

class Print(AST):
    """Print statement node"""
    def __init__(self, token, expr):
        super().__init__(token)
        self.expr = expr

class Compound(AST):
    """Multiple statements node"""
    def __init__(self):
        super().__init__()
        self.children = []

class Block(AST):
    """Code block node (for if/while bodies)"""
    def __init__(self, token, statements):
        super().__init__(token)
        self.statements = statements

class If(AST):
    def __init__(self, condition, if_block, elseif_blocks=None, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.elseif_blocks = elseif_blocks or []  # List of (Condition, Block)
        self.else_block = else_block

class While(AST):
    """While loop node"""
    def __init__(self, token, condition, block):
        super().__init__(token)
        self.condition = condition
        self.block = block

class For(AST):
    """For loop node"""
    def __init__(self, token, init, condition, increment, block):
        super().__init__(token)
        self.init = init
        self.condition = condition
        self.increment = increment
        self.block = block

class Condition(AST):
    """Condition node (for if and while statements)"""
    def __init__(self, left, op, right):
        super().__init__(op)
        self.left = left
        self.op = op
        self.right = right

class NoOp(AST):
    """Empty statement"""
    pass

class StringIndex(AST):
    """String index access node"""
    def __init__(self, string, index):
        super().__init__()
        self.string = string
        self.index = index

# ---- Array Support ----

class ArrayDecl(AST):
    """Array declaration node"""
    def __init__(self, name_token, size_expr):
        super().__init__(name_token)
        self.name = name_token.value
        self.size = size_expr

class ArrayAccess(AST):
    """Array access node"""
    def __init__(self, array_var, index_expr):
        super().__init__(array_var.token)
        self.array = array_var
        self.index = index_expr

class ArrayAssign(AST):
    """Array element assignment node"""
    def __init__(self, array_access, value):
        super().__init__(array_access.token)
        self.array_access = array_access
        self.value = value

# ---- Function Support ----

class FuncDecl(AST):
    """Function declaration node"""
    def __init__(self, name_token, params, body):
        super().__init__(name_token)
        self.name = name_token.value
        self.params = params  # List of Var nodes
        self.body = body      # Block or Compound

class FuncCall(AST):
    """Function call node"""
    def __init__(self, name_token, args):
        super().__init__(name_token)
        self.name = name_token.value
        self.args = args  # List of expressions

class Return(AST):
    """Return statement node"""
    def __init__(self, token, expr):
        super().__init__(token)
        self.expr = expr

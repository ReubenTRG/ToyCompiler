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
    """If statement node"""
    def __init__(self, token, condition, if_block, else_block=None):
        super().__init__(token)
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block
        
class While(AST):
    """While loop node"""
    def __init__(self, token, condition, block):
        super().__init__(token)
        self.condition = condition
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
"""
Interpreter implementation for the Simple Compiler
"""
from lexer.lexer import TokenType
from parser.ast import (
    BinOp, Number, UnaryOp, Var, Assign, 
    Print, Compound, Block, If, While, Condition, NoOp
)

class Interpreter:
    """Evaluate the AST"""
    
    def __init__(self, parser):
        self.parser = parser
        self.variables = {}  # Symbol table for variables
        
    def visit_BinOp(self, node):
        """Evaluate a binary operation"""
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MULTIPLY:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIVIDE:
            right_val = self.visit(node.right)
            if right_val == 0:
                self.error("Division by zero", node)
            return self.visit(node.left) / right_val
            
    def visit_Number(self, node):
        """Return the value of a number node"""
        return node.value
        
    def visit_UnaryOp(self, node):
        """Evaluate a unary operation"""
        if node.op.type == TokenType.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == TokenType.MINUS:
            return -self.visit(node.expr)
            
    def visit_Compound(self, node):
        """Execute multiple statements"""
        for child in node.children:
            self.visit(child)
            
    def visit_NoOp(self, node):
        """Do nothing for empty statements"""
        pass
            
    def visit_Block(self, node):
        """Execute a block of statements"""
        for statement in node.statements:
            self.visit(statement)
            
    def visit_If(self, node):
        """Execute an if statement"""
        if self.visit(node.condition):
            self.visit(node.if_block)
        elif node.else_block:
            self.visit(node.else_block)
            
    def visit_While(self, node):
        """Execute a while loop"""
        while self.visit(node.condition):
            self.visit(node.block)
            
    def visit_Condition(self, node):
        """Evaluate a condition"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if node.op.type == TokenType.EQUAL:
            return left == right
        elif node.op.type == TokenType.NOT_EQUAL:
            return left != right
        elif node.op.type == TokenType.GREATER:
            return left > right
        elif node.op.type == TokenType.LESS:
            return left < right
        elif node.op.type == TokenType.GREATER_EQUAL:
            return left >= right
        elif node.op.type == TokenType.LESS_EQUAL:
            return left <= right
        
        self.error(f"Invalid condition operator: {node.op.type}", node)
            
    def visit_Assign(self, node):
        """Handle variable assignment"""
        var_name = node.left.value
        self.variables[var_name] = self.visit(node.right)
        
    def visit_Var(self, node):
        """Look up variable value"""
        var_name = node.value
        if var_name not in self.variables:
            self.error(f"Undefined variable: {var_name}", node)
        return self.variables[var_name]
        
    def visit_Print(self, node):
        """Handle print statements"""
        value = self.visit(node.expr)
        print(value)
        
    def visit(self, node):
        """Visit a node"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        """Handle unimplemented node types"""
        self.error(f"No visit_{type(node).__name__} method", node)
    
    def error(self, message, node=None):
        """Raise an interpreter error"""
        position = node.position if node else "unknown position"
        raise Exception(f"Runtime error: {message} at {position}")
        
    def interpret(self):
        """Start interpretation"""
        tree = self.parser.parse()
        self.visit(tree)
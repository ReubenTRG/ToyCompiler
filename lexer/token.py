"""
Token definitions for the Simple Compiler
"""

class TokenType:
    """Token types for our language"""
    # Data types
    NUMBER = 'NUMBER'
    
    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    
    # Parentheses
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    
    # Braces for code blocks
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    
    # Variables and assignments
    IDENTIFIER = 'IDENTIFIER'
    ASSIGN = 'ASSIGN'
    SEMICOLON = 'SEMICOLON'
    
    # Keywords
    PRINT = 'PRINT'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    FOR = 'FOR'
    
    # Comparison operators
    EQUAL = 'EQUAL'
    NOT_EQUAL = 'NOT_EQUAL'
    GREATER = 'GREATER'
    LESS = 'LESS'
    GREATER_EQUAL = 'GREATER_EQUAL'
    LESS_EQUAL = 'LESS_EQUAL'

    # Logical operators
    AND = 'AND'  # &&
    OR = 'OR'    # ||
    NOT = 'NOT'  # !
    
    # End of file
    EOF = 'EOF'

class Token:
    """Token representation"""
    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        
    def __str__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.column})"
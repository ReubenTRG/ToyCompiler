"""
Lexer implementation for the Simple Compiler
"""
from .token import Token, TokenType

class Lexer:
    """Breaks input code into tokens"""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None
        
    def advance(self):
        """Move to the next character"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            
    def peek(self):
        """Look at the next character without advancing"""
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
            
    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char and self.current_char.isspace():
            self.advance()
            
    def skip_comment(self):
        """Skip single-line comments"""
        while self.current_char and self.current_char != '\n':
            self.advance()
            
    def get_number(self):
        """Parse a number from the input"""
        result = ""
        line = self.line
        column = self.column
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
            
        # Validate it's a proper number
        try:
            value = float(result)
            return Token(TokenType.NUMBER, value, line, column)
        except ValueError:
            self.error(f"Invalid number format: {result}")
    
    def get_identifier(self):
        """Parse an identifier (variable name, keyword)"""
        result = ""
        line = self.line
        column = self.column
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Check if this is a keyword
        keywords = {
            'print': TokenType.PRINT,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR
        }
        
        token_type = keywords.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, line, column)
            
    def get_next_token(self):
        """Get the next token from input"""
        while self.current_char:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # Skip comments (lines starting with #)
            if self.current_char == '#':
                self.skip_comment()
                continue
                
            # Numbers
            if self.current_char.isdigit():
                return self.get_number()
                
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.get_identifier()
                
            # Operators and symbols
            current_line = self.line
            current_column = self.column
            
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', current_line, current_column)
                
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', current_line, current_column)
                
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', current_line, current_column)
                
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', current_line, current_column)
                
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':  # Check for ==
                    self.advance()
                    return Token(TokenType.EQUAL, '==', current_line, current_column)
                return Token(TokenType.ASSIGN, '=', current_line, current_column)
                
            # In lexer.py, inside the get_next_token() method:

            if self.current_char == '!':
                current_line = self.line
                current_column = self.column
                self.advance()
                if self.current_char == '=':  # Check for !=
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', current_line, current_column)
                return Token(TokenType.NOT, '!', current_line, current_column) # return NOT token if no '='
                            
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':  # Check for >=
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', current_line, current_column)
                return Token(TokenType.GREATER, '>', current_line, current_column)
                
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':  # Check for <=
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', current_line, current_column)
                return Token(TokenType.LESS, '<', current_line, current_column)
                
            # Logical operators
            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token(TokenType.AND, '&&', current_line, current_column)
                else:
                    self.error("Expected '&' after '&'")

            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token(TokenType.OR, '||', current_line, current_column)
                else:
                    self.error("Expected '|' after '|'")

        
            
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', current_line, current_column)
                
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', current_line, current_column)
                
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', current_line, current_column)
                
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', current_line, current_column)
                
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', current_line, current_column)
                
            # Unrecognized character
            self.error(f"Unexpected character: {self.current_char}")
        
        # End of input
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def error(self, message):
        """Raise a lexer error"""
        raise Exception(f"Lexer error: {message} at line {self.line}, column {self.column}")
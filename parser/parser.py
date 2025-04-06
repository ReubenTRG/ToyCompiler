"""
Parser implementation for the Simple Compiler
"""
from lexer.token import TokenType
from .ast import (
    AST, BinOp, Number, UnaryOp, Var, Assign, 
    Print, Compound, Block, If, While, Condition, NoOp, For, String, StringIndex, Array, ArrayAccess,
    FunctionDecl, FunctionCall, Return
)

class Parser:
    """Parse tokens into an AST"""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        
    def error(self, message):
        """Raise a syntax error"""
        line = self.current_token.line if self.current_token else "unknown"
        column = self.current_token.column if self.current_token else "unknown"
        raise Exception(f"Syntax error: {message} at line {line}, column {column}")
        
    def eat(self, token_type):
        """Consume the current token if it matches the expected type"""
        if self.current_token.type == token_type:
            token = self.current_token
            self.current_token = self.lexer.get_next_token()
            return token
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")
            
    def program(self):
        """Program is a list of statements"""
        node = self.compound_statement()
        return node
            
    def compound_statement(self):
        """Handle multiple statements"""
        nodes = Compound()
        
        while self.current_token.type != TokenType.EOF:
            nodes.children.append(self.statement())
            
        return nodes
            
    def statement(self):
        """Parse a statement"""
        if self.current_token.type == TokenType.IDENTIFIER:
            # Check if it's a function call or assignment
            if self.lexer.peek() == '(':  # Look ahead for function call
                node = self.function_call()
                self.eat(TokenType.SEMICOLON)
            else:
                node = self.assignment_statement()
                self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.PRINT:
            token = self.current_token
            node = self.print_statement()
            self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.IF:
            token = self.current_token
            node = self.if_statement()
        elif self.current_token.type == TokenType.WHILE:
            token = self.current_token
            node = self.while_statement()
        elif self.current_token.type == TokenType.FOR:
            token = self.current_token
            node = self.for_statement()
        elif self.current_token.type == TokenType.FUNCTION:
            token = self.current_token
            node = self.function_declaration()
        elif self.current_token.type == TokenType.RETURN:
            token = self.current_token
            node = self.return_statement()
            self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.SEMICOLON:
            # Empty statement
            self.eat(TokenType.SEMICOLON)
            node = NoOp()
        else:
            self.error(f"Unexpected token {self.current_token.type} in statement")
            
        return node

    # Add these new parsing methods
    def function_declaration(self):
        """Parse a function declaration"""
        token = self.eat(TokenType.FUNCTION)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Parse parameters
        self.eat(TokenType.LPAREN)
        params = []
        
        # Handle empty parameter list
        if self.current_token.type != TokenType.RPAREN:
            # First parameter
            param_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            params.append(param_name)
            
            # Additional parameters
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                param_name = self.current_token.value
                self.eat(TokenType.IDENTIFIER)
                params.append(param_name)
        
        self.eat(TokenType.RPAREN)
        
        # Parse function body
        body = self.block()
        
        return FunctionDecl(token, name, params, body)

    def function_call(self):
        """Parse a function call"""
        name = self.current_token.value
        token = self.eat(TokenType.IDENTIFIER)
        
        self.eat(TokenType.LPAREN)
        args = []
        
        # Handle empty argument list
        if self.current_token.type != TokenType.RPAREN:
            # First argument
            args.append(self.expr())
            
            # Additional arguments
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expr())
        
        self.eat(TokenType.RPAREN)
        
        return FunctionCall(token, name, args)

    def return_statement(self):
        """Parse a return statement"""
        token = self.eat(TokenType.RETURN)
        
        # Check if there is an expression to return
        if self.current_token.type != TokenType.SEMICOLON:
            expr = self.expr()
            return Return(token, expr)
        else:
            return Return(token)
    
    def block(self):
        """Parse a code block (between { and })"""
        token = self.eat(TokenType.LBRACE)
        
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.statement())
            
        self.eat(TokenType.RBRACE)
        return Block(token, statements)
    
    def if_statement(self):
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.condition()
        self.eat(TokenType.RPAREN)
        if_block = self.block()

        elseif_blocks = []
        while self.current_token.type == TokenType.ELSEIF:
            self.eat(TokenType.ELSEIF)
            self.eat(TokenType.LPAREN)
            elseif_condition = self.condition()
            self.eat(TokenType.RPAREN)
            elseif_block = self.block()
            elseif_blocks.append((elseif_condition, elseif_block))

        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_block = self.block()

        return If(condition, if_block, elseif_blocks, else_block)

    
    def while_statement(self):
        """Parse a while loop"""
        token = self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.condition()
        self.eat(TokenType.RPAREN)
        
        block = self.block()
        return While(token, condition, block)
    
    def for_statement(self):
        """Parse a for loop"""
        token = self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        
        init = self.assignment_statement() # initialization statement
        self.eat(TokenType.SEMICOLON)

        condition = self.condition() # condition statement, using the same condition parsing.
        self.eat(TokenType.SEMICOLON)

        increment = self.assignment_statement() # increment statement
        self.eat(TokenType.RPAREN)
        
        block = self.block()
        return For(token, init, condition, increment, block)
    
    def condition(self):
        """Parse a condition (for if/while)"""
        # print(f"Parsing condition. Current token: {self.current_token}")
        left = self.expr()
        # print(f"After expr. Left: {left}")

        # Handle comparison operators first
        if self.current_token.type in (
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.GREATER, TokenType.LESS,
            TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL
        ):
            op = self.current_token
            self.eat(op.type)
            right = self.expr()
            left = Condition(left, op, right)
            # print(f"After comparison. Left: {left}")

        # Handle logical operators (AND, OR)
        while self.current_token.type in (TokenType.AND, TokenType.OR):
            op = self.current_token
            self.eat(op.type)
            right = self.expr()
            left = Condition(left, op, right)
            # print(f"After logical op. Left: {left}")

        # Handle NOT operator
        if self.current_token.type == TokenType.NOT:
            op = self.current_token
            self.eat(TokenType.NOT)
            left = Condition(left, op)
            # print(f"After NOT. Left: {left}")

        # print(f"Condition returning: {left}")
        return left
        
    def print_statement(self):
        """Parse a print statement"""
        token = self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        node = Print(token, self.expr())
        self.eat(TokenType.RPAREN)
        return node
        
    def assignment_statement(self):
        """Parse an assignment statement"""
        left = Var(self.current_token)
        token = self.eat(TokenType.IDENTIFIER)
        op = self.eat(TokenType.ASSIGN)
        right = self.expr()
        node = Assign(left, op, right)
        return node
    
    def expr(self):
        """Parse an expression"""
        node = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            else:
                self.eat(TokenType.MINUS)
                
            node = BinOp(node, token, self.term())
            
        return node
    
    def term(self):
        """Parse a term"""
        node = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            else:
                self.eat(TokenType.DIVIDE)
                
            node = BinOp(node, token, self.factor())
            
        return node
    def factor(self):
        """Parse a factor"""
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.LBRACKET:  # Array literal
            return self.array_literal()
        elif token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())
        elif token.type == TokenType.IDENTIFIER:
            token = self.eat(TokenType.IDENTIFIER)
            # Check if it's a function call
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []
                
                # Handle empty argument list
                if self.current_token.type != TokenType.RPAREN:
                    # First argument
                    args.append(self.expr())
                    
                    # Additional arguments
                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.expr())
                
                self.eat(TokenType.RPAREN)
                return FunctionCall(token, token.value, args)
            # Handle array access or string index
            elif self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                index = self.expr()
                self.eat(TokenType.RBRACKET)
                return ArrayAccess(Var(token), index)
            return Var(token)
        elif token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp(token, self.factor())

        self.error(f"Unexpected token {token.type} in factor")

    def array_literal(self):
        """Parse an array literal [elem1, elem2, ...]"""
        token = self.eat(TokenType.LBRACKET)
        elements = []
        
        # Handle empty array
        if self.current_token.type == TokenType.RBRACKET:
            self.eat(TokenType.RBRACKET)
            return Array(token, elements)
        
        # Add first element
        elements.append(self.expr())
        
        # Add remaining elements
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            elements.append(self.expr())
        
        self.eat(TokenType.RBRACKET)
        return Array(token, elements)
        
    def parse(self):
        """Start parsing"""
        return self.program()
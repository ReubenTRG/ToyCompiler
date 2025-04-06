from lexer.token import TokenType
from .ast import (
    AST, BinOp, Number, UnaryOp, Var, Assign, Print, Compound, Block, 
    If, While, Condition, NoOp, For, String, StringIndex,
    ArrayDecl, ArrayAccess, ArrayAssign, FuncDecl, FuncCall, Return
)

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        line = self.current_token.line if self.current_token else "unknown"
        column = self.current_token.column if self.current_token else "unknown"
        raise Exception(f"Syntax error: {message} at line {line}, column {column}")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            token = self.current_token
            self.current_token = self.lexer.get_next_token()
            return token
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def program(self):
        return self.compound_statement()

    def compound_statement(self):
        nodes = Compound()
        while self.current_token.type != TokenType.EOF:
            nodes.children.append(self.statement())
        return nodes

    def statement(self):
        if self.current_token.type == TokenType.IDENTIFIER:
            if self.peek_token().type == TokenType.LPAREN:
                node = self.function_call()
            elif self.peek_token().type == TokenType.LBRACKET:
                node = self.assignment_statement()  # Could be ArrayAssign
            else:
                node = self.assignment_statement()
            self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.PRINT:
            node = self.print_statement()
            self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.IF:
            node = self.if_statement()
        elif self.current_token.type == TokenType.WHILE:
            node = self.while_statement()
        elif self.current_token.type == TokenType.FOR:
            node = self.for_statement()
        elif self.current_token.type == TokenType.FUNCTION:
            node = self.function_declaration()
        elif self.current_token.type == TokenType.RETURN:
            node = self.return_statement()
            self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.VAR:
            node = self.array_declaration()
            self.eat(TokenType.SEMICOLON)
        elif self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            node = NoOp()
        else:
            self.error(f"Unexpected token {self.current_token.type} in statement")
        return node

    def array_declaration(self):
        self.eat(TokenType.VAR)
        name_token = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LBRACKET)
        size_expr = self.expr()
        self.eat(TokenType.RBRACKET)
        return ArrayDecl(name_token, size_expr)

    def peek_token(self):
        saved_pos = self.lexer.pos
        saved_line = self.lexer.line
        saved_column = self.lexer.column
        saved_current = self.lexer.current_char

        next_token = self.lexer.get_next_token()

        self.lexer.pos = saved_pos
        self.lexer.line = saved_line
        self.lexer.column = saved_column
        self.lexer.current_char = saved_current
        return next_token

    def block(self):
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.statement())
        self.eat(TokenType.RBRACE)
        return Block(None, statements)

    def function_declaration(self):
        token = self.eat(TokenType.FUNCTION)
        name_token = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(Var(self.eat(TokenType.IDENTIFIER)))
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                params.append(Var(self.eat(TokenType.IDENTIFIER)))
        self.eat(TokenType.RPAREN)
        body = self.block()
        return FuncDecl(name_token, params, body)

    def function_call(self):
        name_token = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        args = []
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expr())
        self.eat(TokenType.RPAREN)
        return FuncCall(name_token, args)

    def return_statement(self):
        token = self.eat(TokenType.RETURN)
        expr = self.expr()
        return Return(token, expr)

    def assignment_statement(self):
        var = self.variable()
        op = self.eat(TokenType.ASSIGN)
        expr = self.expr()
        if isinstance(var, ArrayAccess):
            return ArrayAssign(var, expr)
        return Assign(var, op, expr)

    def variable(self):
        token = self.eat(TokenType.IDENTIFIER)
        var_node = Var(token)
        while self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            index_expr = self.expr()
            self.eat(TokenType.RBRACKET)
            var_node = ArrayAccess(var_node, index_expr)
        return var_node

    def print_statement(self):
        token = self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        return Print(token, expr)

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
            elseif_cond = self.condition()
            self.eat(TokenType.RPAREN)
            elseif_block = self.block()
            elseif_blocks.append((elseif_cond, elseif_block))

        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_block = self.block()

        return If(condition, if_block, elseif_blocks, else_block)

    def while_statement(self):
        token = self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.condition()
        self.eat(TokenType.RPAREN)
        return While(token, condition, self.block())

    def for_statement(self):
        token = self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        init = self.assignment_statement()
        self.eat(TokenType.SEMICOLON)
        condition = self.condition()
        self.eat(TokenType.SEMICOLON)
        increment = self.assignment_statement()
        self.eat(TokenType.RPAREN)
        return For(token, init, condition, increment, self.block())

    def condition(self):
        left = self.expr()
        if self.current_token.type in (
            TokenType.EQUAL, TokenType.NOT_EQUAL, 
            TokenType.GREATER, TokenType.LESS, 
            TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            op = self.current_token
            self.eat(op.type)
            right = self.expr()
            left = Condition(left, op, right)

        while self.current_token.type in (TokenType.AND, TokenType.OR):
            op = self.current_token
            self.eat(op.type)
            right = self.expr()
            left = Condition(left, op, right)

        return left

    def expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.factor())
        return node

    def factor(self):
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
        elif token.type == TokenType.IDENTIFIER:
            if self.peek_token().type == TokenType.LPAREN:
                return self.function_call()
            return self.variable()
        elif token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT):
            self.eat(token.type)
            return UnaryOp(token, self.factor())
        else:
            self.error(f"Unexpected token {token.type} in factor")

    def parse(self):
        return self.program()
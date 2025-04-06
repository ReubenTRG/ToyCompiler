"""
Interpreter implementation for the Simple Compiler
"""
from lexer.lexer import TokenType
from parser.ast import (
    BinOp, Number, UnaryOp, Var, Assign, 
    Print, Compound, Block, If, While, Condition, NoOp, For, String, StringIndex,
    ArrayDecl, ArrayAccess, ArrayAssign, FuncDecl, FuncCall, Return
)

class Interpreter:
    """Evaluate the AST"""
    
    def __init__(self, parser):
        self.parser = parser
        self.variables = {}  # Symbol table for variables
        self.functions = {}  # Function name -> FuncDecl
        self.call_stack = [] # Call stack for function calls

    def visit_BinOp(self, node):
        if node.op.type == TokenType.PLUS:
            left_val = self.visit(node.left)
            right_val = self.visit(node.right)
            if isinstance(left_val, str) and isinstance(right_val, str):
                return left_val + right_val
            elif isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                return left_val + right_val
            else:
                self.error("Invalid operand types for +", node)
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
        return node.value

    def visit_String(self, node):
        return node.value
        
    def visit_UnaryOp(self, node):
        if node.op.type == TokenType.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == TokenType.MINUS:
            return -self.visit(node.expr)
        elif node.op.type == TokenType.NOT:
            return 0 if self.visit(node.expr) != 0 else 1

    def visit_StringIndex(self, node):
        string = self.visit(node.string)
        index = int(self.visit(node.index))
        if not isinstance(string, str):
            self.error("String index access on non-string type", node)
        if not isinstance(index, int):
            self.error("String index must be integer", node)
        if index < 0 or index >= len(string):
            self.error("String index out of range", node)
        return string[index]
    
    def visit_ArrayDecl(self, node):
        name = node.name.value
        size = self.visit(node.size_expr)
        if not isinstance(size, int) or size < 0:
            self.error("Array size must be a non-negative integer", node)
        self.variables[name] = [0] * size

    def visit_ArrayAccess(self, node):
        array = self.visit(node.array)
        index = self.visit(node.index)
        if not isinstance(array, list):
            self.error("Trying to index a non-array", node)
        if not isinstance(index, int):
            self.error("Array index must be an integer", node)
        if index < 0 or index >= len(array):
            self.error("Array index out of bounds", node)
        return array[index]

    def visit_ArrayAssign(self, node):
        array = self.visit(node.array)
        index = self.visit(node.index)
        value = self.visit(node.value)
        if not isinstance(array, list):
            self.error("Trying to assign to a non-array", node)
        if not isinstance(index, int):
            self.error("Array index must be an integer", node)
        if index < 0 or index >= len(array):
            self.error("Array index out of bounds", node)
        array[index] = value

    def visit_Compound(self, node):
        for child in node.children:
            result = self.visit(child)
            if isinstance(result, ReturnSignal):
                return result

    def visit_NoOp(self, node):
        pass

    def visit_Block(self, node):
        for statement in node.statements:
            result = self.visit(statement)
            if isinstance(result, ReturnSignal):
                return result

    def visit_If(self, node):
        if self.visit(node.condition):
            return self.visit(node.if_block)
        else:
            for elseif_condition, elseif_block in node.elseif_blocks:
                if self.visit(elseif_condition):
                    return self.visit(elseif_block)
            if node.else_block:
                return self.visit(node.else_block)

    def visit_While(self, node):
        while self.visit(node.condition):
            result = self.visit(node.block)
            if isinstance(result, ReturnSignal):
                return result

    def visit_For(self, node):
        self.visit(node.init)
        while self.visit(node.condition):
            result = self.visit(node.block)
            if isinstance(result, ReturnSignal):
                return result
            self.visit(node.increment)

    def visit_Condition(self, node):
        left = self.visit(node.left)
        if node.op:
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
            elif node.op.type == TokenType.AND:
                return left != 0 and right != 0
            elif node.op.type == TokenType.OR:
                return left != 0 or right != 0
            elif node.op.type == TokenType.NOT:
                return left == 0
            else:
                self.error(f"Invalid condition operator: {node.op.type}", node)
        else:
            return left != 0

    def visit_Assign(self, node):
        var_name = node.left.value
        self.variables[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        if var_name not in self.variables:
            self.error(f"Undefined variable: {var_name}", node)
        return self.variables[var_name]

    def visit_Print(self, node):
        value = self.visit(node.expr)
        print(value)

    def visit_FuncDecl(self, node):
        self.functions[node.name.value] = node

    def visit_FuncCall(self, node):
        func_name = node.name.value
        if func_name not in self.functions:
            self.error(f"Function '{func_name}' not defined", node)
        func = self.functions[func_name]

        if len(node.args) != len(func.params):
            self.error("Argument count mismatch", node)

        # Save current variable scope
        saved_variables = self.variables.copy()

        # Setup new scope
        self.variables = {}
        for param, arg in zip(func.params, node.args):
            self.variables[param.value] = self.visit(arg)

        result = self.visit(func.body)
        self.variables = saved_variables

        if isinstance(result, ReturnSignal):
            return result.value
        return None

    def visit_Return(self, node):
        return ReturnSignal(self.visit(node.value))

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        self.error(f"No visit_{type(node).__name__} method", node)

    def error(self, message, node=None):
        position = node.position if node else "unknown position"
        raise Exception(f"Runtime error: {message} at {position}")

    def interpret(self):
        tree = self.parser.parse()
        self.visit(tree)


class ReturnSignal:
    def __init__(self, value):
        self.value = value

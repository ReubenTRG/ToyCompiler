"""
Interpreter implementation for the Simple Compiler
"""
from lexer.lexer import TokenType
from parser.ast import (
    BinOp, Number, UnaryOp, Var, Assign, 
    Print, Compound, Block, If, While, Condition, NoOp, For, String, StringIndex
)

class Interpreter:
    """Evaluate the AST"""
    
    def __init__(self, parser):
        self.parser = parser
        self.variables = {}  # Global symbol table for variables
        self.functions = {}  # Symbol table for functions
        
    # Add these methods to handle functions
    
    def visit_FunctionDecl(self, node):
        """Store a function declaration"""
        self.functions[node.name] = node
        
    def visit_FunctionCall(self, node):
        """Execute a function call"""
        function_name = node.name
        
        if function_name not in self.functions:
            self.error(f"Undefined function: {function_name}", node)
            
        function_node = self.functions[function_name]
        
        # Check argument count
        if len(node.args) != len(function_node.params):
            self.error(f"Function {function_name} expects {len(function_node.params)} arguments, got {len(node.args)}", node)
            
        # Save current scope
        saved_variables = self.variables.copy()
        
        # Create new scope with parameters
        # self.variables = {}
        
        # Evaluate arguments and assign to parameters
        for param_name, arg_node in zip(function_node.params, node.args):
            self.variables[param_name] = self.visit(arg_node)
            
        # Execute function body
        result = None
        try:
            self.visit(function_node.body)
        except ReturnValue as rv:
            result = rv.value
            
        # Restore original scope
        self.variables = saved_variables
        
        return result

    def visit_Return(self, node):
        """Handle return statement"""
        value = None
        if node.expr:
            value = self.visit(node.expr)
        raise ReturnValue(value)
        
    def visit_BinOp(self, node):
        """Evaluate a binary operation"""
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
        """Return the value of a number node"""
        return node.value

    def visit_String(self, node):
        """Return the value of a string node"""
        return node.value
        
    def visit_UnaryOp(self, node):
        """Evaluate a unary operation"""
        if node.op.type == TokenType.PLUS:
            return +self.visit(node.expr)
        elif node.op.type == TokenType.MINUS:
            return -self.visit(node.expr)
        elif node.op.type == TokenType.NOT:
            return 0 if self.visit(node.expr) != 0 else 1 # 0 if the expression is non-zero (true), 1 if it is zero (false).

    def visit_StringIndex(self, node):
        """Handle string index access"""
        string = self.visit(node.string)
        index = int(self.visit(node.index))
        if not isinstance(string, str):
            self.error("String index access on non-string type", node)
        if not isinstance(index, int):
            self.error("String index must be integer", node)
        if index < 0 or index >= len(string):
            self.error("String index out of range", node)
        return string[index]
            
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
        if self.visit(node.condition):
            self.visit(node.if_block)
        else:
            for elseif_condition, elseif_block in node.elseif_blocks:
                if self.visit(elseif_condition):
                    self.visit(elseif_block)
                    return
            if node.else_block:
                self.visit(node.else_block)

            
    def visit_While(self, node):
        """Execute a while loop"""
        while self.visit(node.condition):
            self.visit(node.block)
    
    def visit_For(self, node):
        """Execute a for loop"""
        self.visit(node.init) # initialization
        while self.visit(node.condition): # condition
            self.visit(node.block) # loop body
            self.visit(node.increment) # increment
            
    def visit_Condition(self, node):
        """Evaluate a condition"""
        left = self.visit(node.left)

        if node.op:  # Check if there is an operator
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
                return left != 0 and right != 0  # Non-zero is true
            elif node.op.type == TokenType.OR:
                return left != 0 or right != 0  # Non-zero is true
            elif node.op.type == TokenType.NOT:
                return left == 0  # 0 is false

            else:
                self.error(f"Invalid condition operator: {node.op.type}", node)
        else:
            return left != 0 #handles when a single variable is used as a condition
                
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
        try:
            self.visit(tree)
        except ReturnValue as rv:
            # Function returned outside any function - likely from global scope
            print(f"Warning: Return statement outside of function with value: {rv.value}")

    def visit_Array(self, node):
        """Evaluate an array literal"""
        elements = [self.visit(element) for element in node.elements]
        return elements

    def visit_ArrayAccess(self, node):
        """Handle array element access"""
        array = self.visit(node.array)
        index = int(self.visit(node.index))
        
        if not isinstance(array, list):
            self.error("Array access on non-array type", node)
        if not isinstance(index, int):
            self.error("Array index must be integer", node)
        if index < 0 or index >= len(array):
            self.error("Array index out of range", node)
        
        return array[index]
    
class ReturnValue(Exception):
    """Custom exception to handle return statements"""
    def __init__(self, value=None):
        self.value = value
        super().__init__(str(value))
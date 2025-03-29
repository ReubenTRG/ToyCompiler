#!/usr/bin/env python3
import os
import sys
import argparse

from lexer.lexer import Lexer
from parser.parser import Parser
from interpreter.interpreter import Interpreter

def compile_and_run(code):
    """Compile and run the given code"""
    lexer = Lexer(code)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    
    try:
        interpreter.interpret()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_file(filename):
    """Run code from a file"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        return compile_and_run(code)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Simple Compiler')
    parser.add_argument('file', nargs='?', help='File to compile and run')
    args = parser.parse_args()
    
    if args.file:
        run_file(args.file)
    else:
        # Interactive mode
        print("Simple Compiler Interactive Mode (Ctrl+D to exit)")
        print("Type your code, then press Enter twice to execute:")
        
        while True:
            try:
                lines = []
                print(">>> ", end="")
                
                # Read multiple lines until empty line
                while True:
                    line = input()
                    if not line.strip():
                        break
                    lines.append(line)
                    print("... ", end="")
                    
                if not lines:
                    continue
                    
                code = "\n".join(lines)
                compile_and_run(code)
                
            except EOFError:
                print("\nExiting...")
                break

if __name__ == "__main__":
    main()
from parser import Parser
from lexer import Lexer
from utils import *
from interpreter import Interpreter
from compiler import Compiler

def main():
    # initializing lexer and parser
    lexer   = Lexer()
    parser  = Parser()
    
    # lexing and parsing both files
    main: AST_Program  = parser.run(lexer.run(pre_prossesing(Path('pascal.txt').read_text())))
    lib   = parser.run(lexer.run(pre_prossesing(Path('pascal_lib.txt').read_text())))
    tests = parser.run(lexer.run(pre_prossesing(Path('pascal_test_functions.txt').read_text())))
    
    print(main)
    comp = Compiler(main)
    comp.test(main.connections)
    
    
    # running tests
    test = Interpreter(tests)
    test.run()
    
    # linking files
    #interpreter = Interpreter(main)
    #interpreter.add_lib(lib)
    
    # execute ast
    #interpreter.run()
    
if __name__== "__main__":
    main()
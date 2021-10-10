from parser import Parser
from lexer import Lexer
from utils import *
from interpreter import Interpreter

def main():
    lexer   = Lexer()
    parser  = Parser()
    interpreter = Interpreter(parser.run(lexer.run(pre_prossesing(Path('pascal.txt').read_text()))))
    interpreter.run()
    
    
if __name__== "__main__":
    main()
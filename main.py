from parser import Parser
from lexer import Lexer
from utils import *
from interpreter import Interpreter

lexer   = Lexer()
parser  = Parser()
program = parser.run(lexer.run(pre_prossesing(Path('pascal.txt').read_text())))
interpreter = Interpreter(program)
interpreter.run()
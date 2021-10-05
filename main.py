from parser import Parser
from lexer import Lexer
from utils import *


lexer   = Lexer()
parser  = Parser()
print(parser.run(lexer.run(pre_prossesing(Path('pascal.txt').read_text()))))
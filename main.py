from parser import *
from lexer import *
from utils import *


lexer   = Lexer()
parser  = Parser()
#print(lexer.run(pre_prossesing(Path('pascal.txt').read_text())))
print(parser.run(lexer.run(pre_prossesing(Path('pascal.txt').read_text()))))
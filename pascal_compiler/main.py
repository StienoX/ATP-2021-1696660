from parser import Parser
from lexer import Lexer
from utils import *
from compiler import Compiler

def main():
    args = {}
    try:
        # initializing the arguments parser
        arguments = argparse.ArgumentParser()
        
        # Add arguments to the parser
        arguments.add_argument("-i", "--input", required=True, help="input File")
        arguments.add_argument("-o", "--output", required=True, help="output File")
        args = vars(arguments.parse_args())
    except:
        print("No input was given. Assuming \"pascal.txt\" for input and \"pascal.asm\" for output")
        args = dict([("input","pascal.txt"),("output","pascal.asm")])
    
    # initializing lexer and parser
    lexer   = Lexer()
    parser  = Parser()
    
    # lexing and parsing both files
    main: AST_Program  = parser.run(lexer.run(pre_prossesing(Path(args["input"]).read_text())))

    comp = Compiler(main)
    with open(Path(args["output"]),"w") as output_file:
        output_file.writelines(comp.compile(main))
        print("Compiled: " + str(args["input"] + " to " + str(args["output"]) + " successfully."))
        
    
if __name__== "__main__":
    main()
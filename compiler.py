from utils import *


#
class Compiler():
    def __init__(self, ast: AST_Program):
        self.ast = ast
        self.assembly: List[str] = []
        
    # get_declarations :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_declarations(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Var))
    
    # get_declarations :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_params(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_FunctionParameter))
    
    def run(self):
        return '\n'.join(compile(self.ast,self.assembly)[1]) # this needs to be written to the asm file
    
    def compile(asts, assembly):
        # run each compile function and return the asts and generated assembly.
        return (asts, assembly)
    
    def c_main(self, asts:List[AST_Node], assembly:List[str]) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_Program)):
            assembly = assembly + ["    b .main"] # add branch to the main of the program
            asts = asts[0].connections
        return (asts,assembly)
    
    def c_begin(self, asts:List[AST_Node], assembly:List[str]) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_Begin)):
            asts = asts[0].connections + asts  # add child connections to the ast
        return (asts,assembly)
    
    def c_function_def(self, asts:List[AST_Node], assembly:List[str]) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_Function)):
            rslt_d = self.get_declarations(asts[0])
            rslt_p = self.get_params(asts[0])
            n = (len(rslt_d[0]) + len(rslt_p[0]))
            rslt = "    push  {" 
            if n <= 4: # when using less then 4 variables we use registers
                if n > 1:
                    rslt += "r4, " 
                if n > 2:
                    rslt += "r5, "
                if n > 3:
                    rslt += "r6, "
            if n >= 4:
                rslt += "r7, "
            rslt += "lr}"
            rslt = [rslt]
            if n > 4: # when using more then 4 variables we use the stack
                rslt = rslt + ["    sub  sp, sp, #" + str(n*4)]
                rslt = rslt + ["    add  r7, sp, #0"]
            
            assembly = assembly + [asts[0].procedure_name + ":"] + rslt
            asts = asts[0].connections + asts
            
from utils import *


#
class Compiler():
    def __init__(self, ast: AST_Program):
        self.ast = ast
        self.assembly: List[str] = []
        self.labels = {} # dict stores all the labels generated in assembly
        self.scope = {} # dict stores the current variables as follows: (store function,load function) example call: assembly_instruction = scope[var_name][1]("r0") This will store the contents of r0 somewhere safe
        
    # get_declarations :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_declarations(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Var))
    
    # get_params :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_params(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_FunctionParameter))
    
    # get_declarations_nested :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_declarations_nested(self, asts:List[AST_Node]) -> List[AST_Var]:
        rslt = split_list_if(asts, lambda x: isinstance(x, AST_Var))
        connection_rslts:List[Tuple[List[AST_Node],List[AST_Node]]] = list(map(self.get_declarations_nested,rslt[1]))
        return list(zip(*([rslt] + connection_rslts)))[0]
    
    def run(self):
        return '\n'.join(compile(self.ast,self.assembly,self.scope,self.labels)[1]) # this result needs to be written to a asm file
    
    def compile(asts, assembly, labels, scope):
        # run each compile function and return the asts and generated assembly.
        return (asts, assembly, labels, scope)
    
    def c_main(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_Program)):
            assembly = assembly + ["    b .main"] # add branch to the main of the program
            asts = asts[0].connections
        return (asts,assembly)
    
    def c_begin(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_Begin)):
            asts = asts[0].connections + asts  # add child connections to the ast
        return (asts, assembly, labels, scope)
    
    
    def c_function_def(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        def c_vars(asts:List[AST_Node], scope: dict, n: int, n_p: int, i: int) -> Tuple[List[AST_Node], List[str]]:
            if (isinstance(asts[0],AST_Var)):
                if n_p + i >= n: 
                    return scope
                if n > 4:
                    scope[asts[0].var_name] = (lambda Rx: "    mov  r"+(n_p+4+i)+", " + Rx, lambda Rx: "    mov   " + Rx + ", r" + (n_p+4+i))
                else:
                    scope[asts[0].var_name] = (lambda Rx: "    str  " + Rx + ", [r7,#"+(n_p+i)*4+"]",       lambda Rx: "    ldr   " + Rx + ", [r7,#"+(n_p+i)*4+"]")
                return c_vars(asts[1:], scope, n, n_p, i+1)
            assert() # this should not be abled to happen since we only provide it with AST_Var's
        if (isinstance(asts[0],AST_Function)):
            rslt_d:Tuple[List[AST_Var],List[AST_Node]] = self.get_declarations_nested(asts[0]) # number of var declarations ((nested) forward lookup)
            rslt_p = self.get_params(asts[0]) # number of parameters (forward lookup)
            n_p = len(rslt_p[0])
            n = (len(rslt_d[0]) + n_p)
            rslt = "    push  {"
            tmp_rslt = []
            if n <= 4: # when using less then 4 variables we use registers
                if n_p >= 1:
                    rslt += "r4, "
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    mov  r4, " + Rx, lambda Rx: "    mov   " + Rx + ", r4")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r0")]
                if n_p >= 2:
                    rslt += "r5, "
                    scope[rslt_p[0][1].parameter_name] = (lambda Rx: "    mov  r5, " + Rx, lambda Rx: "    mov   " + Rx + ", r5")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r1")]
                if n_p >= 3:
                    rslt += "r6, "
                    scope[rslt_p[0][2].parameter_name] = (lambda Rx: "    mov  r6, " + Rx, lambda Rx: "    mov   " + Rx + ", r6")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r2")]
            if n >= 4:
                rslt += "r7, " # we always allocate r7 either for stack offset use or to store the 4th parameter/var
                if n == 4 and n_p == 4:
                    scope[rslt_p[0][3].parameter_name] = (lambda Rx: "    mov  r7, " + Rx, lambda Rx: "    mov   " + Rx + ", r7")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r3")]
            rslt += "lr}"
            rslt = [rslt] + tmp_rslt
            if n > 4: # when using more then 4 variables we use the stack
                rslt = rslt + ["    sub  sp, sp, #" + str(n*4)]
                rslt = rslt + ["    add  r7, sp, #0"] # using add because sp does not support mov
                #scope[] need to add load and store to the stack
                if n_p >= 1:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str  " + Rx + ", [r7]",       lambda Rx: "    ldr   " + Rx + ", [r7]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r0")]
                if n_p >= 2:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str  " + Rx + ", [r7, #4]",   lambda Rx: "    ldr   " + Rx + ", [r7, #4]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r1")]
                if n_p >= 3:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str  " + Rx + ", [r7, #8]",   lambda Rx: "    ldr   " + Rx + ", [r7, #8]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r2")]
                if n_p >= 4:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str  " + Rx + ", [r7, #12]",  lambda Rx: "    ldr   " + Rx + ", [r7, #12]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r3")]
            
            scope = c_vars(rslt_d[0],scope,n,n_p,0) # updating scope for the rest of the variables
                
            assembly = assembly + [asts[0].procedure_name + ":"] + rslt
            labels[asts[0].procedure_name] = n_p # currently stores num of parameters labels also needs to store loops and if statements. loops, if statements or functions without parameters will contain 0 as num of parameters
            asts = asts[0].connections + asts
            
            # call next compile functions
            
            # TODO
        return (asts, assembly, labels, scope) # we are not in a function definition
            
    def c_function_call(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_FunctionCall)):
            pre_result = []
            rslt = []
            
            #if arg._type == 'identifier':
                # load from stack or register use scope.
            #if arg._type == 'digit':
                # load const to r+number of param place
            #if arg._type == 'expression':
                # call c_expression
            #if arg._type == 'string':
                # not supported
            params = list(map(lambda function_param: function_param ,asts[0].connections))

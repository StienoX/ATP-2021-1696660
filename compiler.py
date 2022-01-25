from utils import *


# 
class Compiler():
    def __init__(self, ast: AST_Program):
        self.ast = ast
        self.assembly: List[str] = []
        self.labels = {} # dict stores all the labels generated in assembly
        self.scope = {} # dict stores the current variables as follows: (store function,load function) example call: assembly_instruction = scope[var_name][1]("r0") This will store the contents of r0 somewhere safe
    
    def generate_assembly_from_list(self, assembly_lst:List[str]) -> str:
        return "\n".join(assembly_lst)
    
    # a tempory test function that will only be used for debugging
    def test(self, ast):
        ast_head = ast[0]
        if isinstance(ast_head, AST_Function):
            rslt = (self.c_function_def([ast_head], [], {}, {}))
            print(self.generate_assembly_from_list(rslt[1]))
            #print(self.get_loads(ast_head)) 
            #print(len(self.get_declarations_nested(ast_head)))
        else:
            return self.test(ast[1:]) # skip till main
        return "DONE"
    # generate_new_label :: dict -> Tuple(str,dict)
    def generate_new_label(self, labels: dict) -> Tuple[str,dict]:
        def new_label(label_name, labels):
            if label_name in labels:
                return new_label("L" + str((int(label_name[1:]) + 1)), labels)
            return label_name
        label_name = new_label("L1",labels)
        labels[label_name] = 0
        return (label_name + ":",labels)
    
    # get_declarations :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_declarations(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Var))
    
    # get_params :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_params(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_FunctionParameter))
    
    # get_params :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_body(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Begin))
    
    # get_declarations_nested :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_loads(self,asts:List[AST_Node]) -> int:
        def _get_expressionAST(asts:List[AST_Node]) -> List[AST_Var]:
            rslt = split_list_if(asts, lambda x: isinstance(x, AST_Expression))
            return functools.reduce(lambda x, y: x + y, list(map(_get_expressionAST,rslt[1])), rslt[0])
        expressions = _get_expressionAST(asts)
        def _count(expression:Union[ExprNode,ExprLeaf], i = 0) -> int:
            if (isinstance(expression.right,ExprNode) or expression.right.type == "func_call") and (isinstance(expression.left,ExprNode) or expression.left.type == "func_call"):
                i += 1
                expression.e_value = i # sets the depth of the node in the tree which to use within the scope
                if isinstance(expression.left,ExprNode):
                    i = _count(expression.left, i)
                if isinstance(expression.right,ExprNode):
                    i = _count(expression.right, i)
                return i
            elif isinstance(expression.right,ExprNode):
                return _count(expression.right, i)
            elif isinstance(expression.left,ExprNode):
                return _count(expression.left, i)
            else:
                return i
        lst = list(map(lambda top_node: _count(top_node.right),expressions))
        return max(lst) if lst else 0
        
    # get_declarations_nested :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_declarations_nested(self, asts:List[AST_Node]) -> List[AST_Var]:
        rslt = split_list_if(asts, lambda x: isinstance(x, AST_Var))
        return functools.reduce(lambda x, y: x + y, list(map(self.get_declarations_nested,rslt[1])), rslt[0])
    
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
    
    def c_body(self, function_asts:List[AST_Node], assembly:List[str], labels:dict, scope:dict)-> Tuple[List[AST_Node],List[str],dict,dict]:
        if function_asts:
            if len(function_asts) > 1:
                (_, assembly, labels, scope) = self.c_body([function_asts[0]], assembly, labels, scope)
                return self.c_body(function_asts[1:], assembly, labels, scope)
            if isinstance(function_asts[0], AST_Var):
                return self.c_body(function_asts[1:], assembly, labels, scope)
            if isinstance(function_asts[0], AST_Expression):
                return self.c_body(*self.c_expression([function_asts[0]], assembly, labels, scope))
            if isinstance(function_asts[0], AST_If):
                return self.c_body(*self.c_if_statement([function_asts[0]], assembly, labels, scope))
            if isinstance(function_asts[0], AST_FunctionCall):
                return self.c_body(*self.c_function_call([function_asts[0]], assembly, labels, scope))
            if isinstance(function_asts[0], AST_IfTrue) or isinstance(function_asts[0], AST_IfFalse):
                return self.c_body(function_asts[0].connections, assembly, labels, scope) 
        else:
            return (function_asts, assembly, labels, scope)
    
    
    def c_function_def(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        def c_vars(asts:List[AST_Node], scope: dict, n: int, n_p: int, n_e: int,i: int) -> Tuple[List[AST_Node], List[str]]:
            if asts and (isinstance(asts[0],AST_Var)):
                if n_p + i >= n - n_e:
                    return scope
                if n <= 4:
                    scope[asts[0].var_name] = (lambda Rx: "    mov r"+str(n_p+4+i)+", " + Rx, lambda Rx: "    mov " + Rx + ", r" + str(n_p+4+i))
                else:
                    scope[asts[0].var_name] = (lambda Rx: "    str " + Rx + ", [r7,#"+str((n_p+i)*4)+"]",       lambda Rx: "    ldr " + Rx + ", [r7,#"+str((n_p+i)*4)+"]")
                return c_vars(asts[1:], scope, n, n_p, n_e, i+1)
            return scope
            
        def c_expression(scope: dict, n: int, n_offset: int, i: int) -> Tuple[List[AST_Node], List[str]]:
            if n_offset + i >= n: 
                return scope
            if n <= 4:
                scope[str("E"+str(i))] = (lambda Rx: "    mov r"+str(n_offset+4+i)+", " + Rx, lambda Rx: "    mov " + Rx + ", r" + str(n_offset+4+i))
            else:
                scope[str("E"+str(i))] = (lambda Rx: "    str " + Rx + ", [r7,#"+str((n_offset+i)*4)+"]",       lambda Rx: "    ldr " + Rx + ", [r7,#"+str((n_offset+i)*4)+"]")
            return c_expression(scope, n, n_offset, i+1)
        
        
        if (isinstance(asts[0],AST_Function)):
            previous_scope = deepcopy(scope)
            rslt_d:List[AST_Var] = self.get_declarations_nested(asts[0]) # number of var declarations ((nested) forward lookup)
            rslt_p = self.get_params(asts[0]) # number of parameters (forward lookup)
            n_d = len(rslt_d) # number of variable declarations
            n_p = len(rslt_p[0]) # number of parameters
            n_e = self.get_loads(asts[0]) # the maximum number of used registers (or stack space) simultaneous in use by expressions
            n = (n_d + n_p + n_e) # the number total used registers in this function
            rslt = "    push { r4"  if n else "    push { lr }"# push r4 for either first parameter or saving the stack pointer
            tmp_rslt = []
            if n <= 4: # when using less then 3 variables we use registers (one for storing lr)
                if n_p >= 1:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    mov r4, " + Rx, lambda Rx: "    mov " + Rx + ", r4") # store and load functions for the first parameter
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r0")] # get the str function and store the parameter in a save register
                if n_p >= 2:
                    scope[rslt_p[0][1].parameter_name] = (lambda Rx: "    mov r5, " + Rx, lambda Rx: "    mov " + Rx + ", r5")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r1")]
                if n_p >= 3:
                    scope[rslt_p[0][2].parameter_name] = (lambda Rx: "    mov r6, " + Rx, lambda Rx: "    mov " + Rx + ", r6")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r2")]
                if n_p >= 4:
                    scope[rslt_p[0][2].parameter_name] = (lambda Rx: "    mov r7, " + Rx, lambda Rx: "    mov " + Rx + ", r7")
                    tmp_rslt = tmp_rslt + [scope[rslt_p[0][0].parameter_name][0]("r3")]
                rslt += ", ".join(["","r5","r6","r7"][:n]) # generates a string containing the used registers in this function. The amount is based off the n value
            rslt += ", lr }" if n else ""
            rslt = [rslt] + tmp_rslt
            if n > 4: # when using more then 4 variables we use the stack
                rslt = rslt + ["    sub sp, sp, #" + str(n*4)]
                rslt = rslt + ["    add r4, sp, #0"] # using add because sp does not support mov
                #scope[] need to add load and store to the stack
                if n_p >= 1:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r7]",       lambda Rx: "    ldr   " + Rx + ", [r7]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r0")]
                if n_p >= 2:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r7, #4]",   lambda Rx: "    ldr   " + Rx + ", [r7, #4]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r1")]
                if n_p >= 3:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r7, #8]",   lambda Rx: "    ldr   " + Rx + ", [r7, #8]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r2")]
                if n_p >= 4:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r7, #12]",  lambda Rx: "    ldr   " + Rx + ", [r7, #12]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r3")]
            
            scope = c_vars(rslt_d,scope,n,n_p,n_e,0) # updating scope for the variables
            scope = c_expression(scope,n,n_p+n_d,0) # updating scope for the expression stores/loads when an operator has an operator for both childs
            assembly = assembly + [asts[0].procedure_name + ":"] + rslt # prepend the procedure name
            labels[asts[0].procedure_name] = (n_p, list(map(lambda x: str(x.type), rslt_p[0]))) # currently stores num of parameters labels and sets the label active also needs to store loops and if statements. loops, if statements or functions without parameters will contain 0 as num of parameters
            scope[asts[0].procedure_name] = (lambda _: "    pop { " + ", ".join(["r4","r5","r6","r7"][:n if n <= 4 else 3]) + "".join([", ", "pc }"][int(not(n)):]) , lambda Rx: "function call")
            # call next compile functions (with the connections of the function)
            (_, assembly, labels, scope) = self.c_function_body(asts[0].connections, assembly, labels, scope)
            return (asts[1:], assembly, labels, previous_scope)
        return (asts, assembly, labels, scope) # we are not in a function definition
            
    def c_function_call(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_FunctionCall)):
            if len(asts[0].connections) == 4:
                if len(asts[0][3].connections):
                    expr_assembly = self.c_expression([asts[0][3][0]], [], labels, scope) # expression inside function call for the parameter
                    assembly += expr_assembly[1] + ["    mov r3, r0"]      
                elif asts[0][3].type == "pvar":
                    assembly += [scope[str(asts[0][3].value)][1]("r3")]
                else:
                    assembly += ["    mov r3, #" + str(asts[0][3].value)] # const value
            if len(asts[0].connections) >= 3:
                if len(asts[0][2].connections):
                    expr_assembly = self.c_expression([asts[0][2][0]], [], labels, scope)
                    assembly += expr_assembly[1] + ["    mov r2, r0"]
                elif asts[0][2].type == "pvar":
                    assembly += [scope[str(asts[0][2].value)][1]("r2")]  
                else:
                    assembly += ["    mov r2, #" + str(asts[0][2].value)] # const value
            if len(asts[0].connections) >= 2:
                if len(asts[0][1].connections):
                    expr_assembly = self.c_expression([asts[0][1][0]], [], labels, scope)
                    assembly += expr_assembly[1] + ["    mov r1, r0"]
                elif asts[0][1].type == "pvar":
                    assembly += [scope[str(asts[0][1].value)][1]("r1")]
                else:
                    assembly += ["    mov r1, #" + str(asts[0][1].value)] # const value  
            if len(asts[0].connections) >= 1:
                if len(asts[0][0].connections):
                    expr_assembly = self.c_expression([asts[0][0][0]], [], labels, scope)
                    assembly += expr_assembly[1]
                elif asts[0][0].type == "pvar":
                    assembly += [scope[str(asts[0][0].value)][1]("r0")]
                else:
                    assembly += ["    mov r0, #" + str(asts[0][0].value)] # const value
            print(assembly)
            print(asts[0])
            return (asts[1:], assembly + ["    b "+ asts[0]._function], labels, scope)
        return (asts, assembly, labels, scope)
            

    
    def c_if_statement(self, asts:List[AST_Node], assembly:List[str], labels:dict, scope:dict) -> Tuple[List[AST_Node],List[str],dict,dict]:
        if isinstance(asts[0], AST_If):
            (label_start_false,labels) = self.generate_new_label(labels)
            (label_end_false,labels) = self.generate_new_label(labels)
            # add expression evalution
            (_,assembly, labels, scope) = self.c_body((split_list_if(asts[0].connections, lambda x: isinstance(x, AST_Expression))[0]), assembly, labels, scope)
            assembly += ["    bne "+str(label_start_false[:-1])]
            (_,assembly, labels, scope) = self.c_body((split_list_if(asts[0].connections, lambda x: isinstance(x, AST_IfTrue))[0]), assembly, labels, scope)
            assembly += ["    b "+str(label_end_false[:-1])]
            assembly += [label_start_false]
            (_,assembly, labels, scope) = self.c_body((split_list_if(asts[0].connections, lambda x: isinstance(x, AST_IfFalse))[0]), assembly, labels, scope)
            assembly += [label_end_false]
            return (asts[1:], assembly, labels, scope)
        return (asts, assembly, labels, scope)
    
    def c_expression(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        
        if (isinstance(asts[0],AST_Expression)):
            #r1 = left
            #r2 = right
            def _c_expression(current_node, return_register, _assembly): # this generates the assembly instructions for the instruction
                if isinstance(current_node, ExprNode):
                    if isinstance(current_node.right, ExprLeaf) and isinstance(current_node.left, ExprLeaf) and current_node.left.type == current_node.right.type and current_node.right.type not in ["func_call","var"]:
                        rslt = 0
                        #optimize by precalculating result of const value's when possible. This happens when both leafs of the current node are const
                        if current_node.data == "*":
                            rslt = int(current_node.left.data) * int(current_node.right.data)
                        elif current_node.data == "+":
                            rslt = int(current_node.left.data) + int(current_node.right.data)
                        elif current_node.data == "-":
                            rslt = int(current_node.left.data) - int(current_node.right.data)
                        elif current_node.data == "/":
                            rslt = int(current_node.left.data) / int(current_node.right.data)
                        _assembly = ["    mov " + return_register + ", #" + str(rslt)] + _assembly
                        return _assembly
                    else:
                        
                        # get the instruction
                        temp_assembly = ""
                        if current_node.data == "*":
                            temp_assembly = "    mul " + return_register + ", "
                        elif current_node.data == "+":
                            temp_assembly = "    add " + return_register + ", "
                        elif current_node.data == "-":
                            temp_assembly = "    sub " + return_register + ", "
                        elif current_node.data == "/":
                            assert() # not implementing this
                            temp_assembly = "  ? div " + return_register + ", "
                        else:
                            print(current_node.data)
                            assert() # unknown/unexpected operator
                         
                        
                        if current_node.left.type == "var" and current_node.right.type == "var":
                            return [scope[current_node.left.data][1]("r1"),scope[current_node.left.data][1]("r2"),temp_assembly + "r1, r2"] + _assembly # might needs to swapped for sub
                        
                        elif current_node.left.type == "var" and current_node.right.type not in ["func_call","var"] and isinstance(current_node.right, ExprLeaf):
                            return [scope[current_node.left.data][1]("r2"),"    mov r1, #" + str(current_node.right.data),temp_assembly + "r1, r2"] + _assembly
                        elif current_node.right.type == "var" and current_node.left.type not in ["func_call","var"] and isinstance(current_node.left, ExprLeaf):
                            return [scope[current_node.right.data][1]("r1"),temp_assembly + "r1, #" + str(current_node.left.data)] + _assembly
                        
                        
                        
                        elif isinstance(current_node.left, ExprLeaf) and current_node.left.type not in ["func_call","var"]: # left side is a const value
                            temp_assembly = temp_assembly + "r2, #" + str(current_node.left.data)
                            _assembly = [temp_assembly] + _assembly
                            return _c_expression(current_node.right,"r2",_assembly)
                           
                        elif isinstance(current_node.right, ExprLeaf) and current_node.right.type not in ["func_call","var"]:
                            temp_assembly = temp_assembly + "r1, #" + str(current_node.right.data)
                            _assembly = [temp_assembly] + _assembly
                            return _c_expression(current_node.left,"r1",_assembly)
                        
                        elif isinstance(current_node.left, ExprLeaf) and current_node.left.type == "var":
                            temp_assembly = temp_assembly + "r1"
                            _assembly = [scope[current_node.left.data][1]("r1"),temp_assembly] + _assembly
                            return _c_expression(current_node.right,"r2",_assembly)
                        
                        elif isinstance(current_node.right, ExprLeaf) and current_node.right.type == "var":
                            temp_assembly = temp_assembly + "r2"
                            _assembly = [scope[current_node.right.data][1]("r2"),temp_assembly] + _assembly
                            return _c_expression(current_node.left,"r1",_assembly)
                        
                        elif isinstance(current_node.left, ExprLeaf) and current_node.left.type == "func_call":
                            temp_assembly = temp_assembly + "r1"
                            _assembly = [scope[current_node.left.data][1]("r1"),temp_assembly] + _assembly
                            return _c_expression(current_node.right,"r2",_assembly)
                        
                        elif isinstance(current_node.right, ExprLeaf) and current_node.right.type == "func_call":
                            temp_assembly = temp_assembly + "r2"
                            _assembly = [scope[current_node.right.data][1]("r2"),temp_assembly] + _assembly
                            return _c_expression(current_node.left,"r1",_assembly)

                        
                        else:
                            _assembly = [temp_assembly + ("r1, r2" if current_node.left.type is not "func_call" else "r0, r2")] + _assembly
                            # load from stack / register
                            _assembly = [scope["E"+str(current_node.e_value-1)][1]("r2")] + _assembly
                            #store[0] load[1]
                            if current_node.left.type is not "func_call":
                                _assembly = _c_expression(current_node.left, "r1", _assembly)
                            else:
                                _assembly = self.c_function_call([current_node.left], [], labels, scope)[1] + _assembly
                            # store to stack / register
                            
                            _assembly = [scope["E"+str(current_node.e_value-1)][0]("r2" if current_node.right.type is not "func_call" else "r0")] + _assembly
                            
                            if current_node.right.type is not "func_call":
                                _assembly = _c_expression(current_node.right, "r2", _assembly)
                            else:
                                _assembly = self.c_function_call([current_node.left], [], labels, scope)[1] + _assembly
                                
                            return _assembly
                else:
                    assert("Error: Invalid Expression.")
                
            top_node = asts[0].right
            if (isinstance(top_node, ExprNode)):
                if top_node.data == ":=": # assignment to var
                    if isinstance(top_node.right, ExprLeaf): # simple assignment (x := 4) 
                        assembly = assembly + [scope[top_node.left.data][0]("#" + str(top_node.right.data))]
                    else:
                        assembly = assembly + _c_expression(top_node.right,"r0",[]) + [scope[top_node.left.data][0]("r0")]
                    return (asts[1:],assembly,labels,scope)
                elif top_node.data == "=": # comparison 
                    temp_assembly = ""
                    
                    if isinstance(top_node.right, ExprLeaf) and isinstance(top_node.left, ExprLeaf):
                        if top_node.right.type == "var" and top_node.left.type == "var":
                            assembly += [scope[top_node.right.data][1]("r2"),scope[top_node.left.data][1]("r1")]
                            temp_assembly = "    cmp r1, r2"
                        elif top_node.right.type == "var" and top_node.left.type != "func_call":
                            assembly += [scope[top_node.right.data][1]("r1")]
                            temp_assembly = "    cmp r1, #" + str(top_node.left.data)
                        elif top_node.left.type == "var" and top_node.right.type != "func_call":
                            assembly += [scope[top_node.left.data][1]("r1")]
                            temp_assembly = "    cmp r1, #" + str(top_node.right.data)
                        elif top_node.left.type == "func_call":
                            pass
                            assembly += ["    b .functioncall thing (needs to call self.c_function_call)"]
                            temp_assembly += "r0"
                        else:
                            temp_assembly += "#" + str(top_node.right.data)
                    elif isinstance(top_node.left, ExprLeaf):
                        if top_node.left.type == "var":
                            assembly += _c_expression(top_node.right,"r2",[]) + [scope[top_node.left.data][1]("r1")]
                            temp_assembly = "    cmp r1, r2"
                        elif top_node.left.type == "func_call":
                            pass
                        else:
                            assembly += _c_expression(top_node.right,"r1",[])
                            assembly += ["    cmp r1, #" + str(top_node.left.data)]
                    elif isinstance(top_node.right, ExprLeaf):
                        if top_node.right.type == "var":
                            assembly += _c_expression(top_node.left,"r2",[]) + [scope[top_node.right.data][1]("r1")]
                            temp_assembly = "    cmp r1, r2"
                        elif top_node.left.type == "func_call":
                            pass
                        else:
                            temp_assembly += "    cmp r1, #" + str(top_node.right.data)
                            assembly += _c_expression(top_node.left,"r1",[])
                    else: 
                        _assembly = [scope["E"+str(top_node.e_value-1)][1]("r2")]
                        _assembly = _c_expression(top_node.left, "r1", _assembly)
                        _assembly = [scope["E"+str(top_node.e_value-1)][0]("r2")] + _assembly
                        _assembly = _c_expression(top_node.right, "r2", _assembly)
                        assembly += _assembly
                        temp_assembly = "    cmp r1, r2"
                    assembly += [temp_assembly]
 
                    return (asts[1:],assembly,labels,scope)
                else:
                    return (asts[1:], assembly + _c_expression(top_node,"r0",[]) ,labels,scope)  
            else:
                return (asts[1:], assembly, labels, scope) # useless expression we dont need to generate any assembly for this since it does not change anything. Example of an useless expression is: (5)
        return (asts, assembly, labels, scope)
    
    def c_function_body(self, asts:List[AST_Node], assembly:List[str], labels:dict, scope:dict) -> Tuple[List[AST_Node],List[str],dict,dict]:
        (body, _) = self.get_body(asts)
        if isinstance(body[0], AST_Begin):
            connections:AST_Node = body[0].connections
            return self.c_body(connections, assembly, labels, scope)
        else:
            assert("No body found in function")
        return ([], assembly, labels, scope)
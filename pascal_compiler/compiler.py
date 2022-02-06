from xml.dom.minidom import TypeInfo
from utils import *


# CLASS : Compiler
# Brief : This class implements internal compiler functionality for pascal language
# Internal compile functions use the following input: 
# [ast] - a list of ast nodes needed to compile.
# assembly - A list of strings containing the generated assembly line by line.
# labels - A dictionary containing the used branch labels generated in assembly. Currently not containing any usefull information other then storing used labels. Could be used in future optimizations. 
# scope - A dictionary cotaining variables. These can be named or unnamed. Unnamed variables are used inside expressions. These use the the following key structure: E + Number
# scope - returns a tuple of function expecting each a single string as input. 
# The first function is store. This function will safely store the value into the register passed into the function.
# The second function is load. This function will retore a previously stored value into the register passed into the function.
class Compiler():
    
    # initialization function for the compiler class
    def __init__(self):
        pass
    
    # Main compile function. Provide an Program ast as head as parameter. The program ast can be generated using the Parser class.
    # compile :: AST_Node -> str
    def compile(self, ast: AST_Node) -> str:
        return self.generate_assembly_from_list(["    .cpu cortex-m0\n    .text\n    .align 4"] + functools.reduce(lambda info,function_def: tuple(list(self.c_function_def([function_def], info[0], info[1], {}))[1:-1]),self.get_functions(ast.connections)[0],([],{}))[0]) if isinstance(ast, AST_Program) else "Error invalid AST"

    # Helper function for joining the multi line assembly into one long string
    # generate_assembly_from_list :: [str] -> str
    def generate_assembly_from_list(self, assembly_lst:List[str]) -> str:
        return "\n".join(assembly_lst)
    
    # Helper function for generating a new unused label
    # generate_new_label :: dict -> Tuple(str,dict)
    def generate_new_label(self, labels: dict) -> Tuple[str,dict]:
        def new_label(label_name, labels):
            if label_name in labels:
                return new_label("L" + str((int(label_name[1:]) + 1)), labels)
            return label_name
        label_name = new_label("L1",labels)
        labels[label_name] = 0
        return (label_name + ":",labels)
    
    # Helper function for getting all functions in a list of asts.
    # get_functions :: [AST_Node] -> ([AST_Function],[AST_Node])
    def get_functions(self, asts:List[AST_Node]) -> Tuple[List[AST_Function],List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Function))
    
    # Helper function for getting all variable declarations in a list of asts.
    # get_declarations :: [AST_Node] -> ([AST_Var],[AST_Node])
    def get_declarations(self, asts:List[AST_Node]) -> Tuple[List[AST_Var],List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Var))
    
    # Helper function for getting all functionparameters in a list of asts.
    # get_params :: [AST_Node] -> ([AST_FunctionParameter],[AST_Node])
    def get_params(self, asts:List[AST_Node]) -> Tuple[List[AST_FunctionParameter],List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_FunctionParameter))
    
    # Helper function for getting all Begin blocks in a list of asts. (useally just one)
    # get_body :: [AST_Node] -> ([AST_Begin],[AST_Node])
    def get_body(self, asts:List[AST_Node]) -> Tuple[List[AST_Begin],List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Begin))
    
    # This function calculates the amount of space we need to reserve for expressions (unamed variables). 
    # This is calculated by getting all expressions inside a function, then calculating for each expression how many nested junctions there are.
    # A junction is am operator where both of the children are operators themselves.
    # When the junction count for each expression is calculated return the highest number.
    # This function returns 0 when there are no expressions.
    # get_loads :: [AST_Node] -> int
    def get_loads(self,asts:List[AST_Node]) -> int:
        def _get_expressionAST(asts:List[AST_Node]) -> List[AST_Var]:
            rslt = split_list_if(asts, lambda x: isinstance(x, AST_Expression))
            return functools.reduce(lambda x, y: x + y, list(map(_get_expressionAST,rslt[1])), rslt[0]) ## getting all expressions this reduce ensures that we also get the nested expressions. (the ones in if statements or in other blocks inside the current function)
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
        
    # The same as the get declaration function but also checks for nested declarations. (decls inside other code blocks)
    # get_declarations_nested :: [AST_Node] -> [AST_Var]
    def get_declarations_nested(self, asts:List[AST_Node]) -> List[AST_Var]:
        rslt = split_list_if(asts, lambda x: isinstance(x, AST_Var))
        return functools.reduce(lambda x, y: x + y, list(map(self.get_declarations_nested,rslt[1])), rslt[0])
    
    # An unused compile function that would compile a main. (first global begin block). Currently unused since we use the main inside main.cpp.
    # c_main :: [AST_Node] -> [str] -> dict -> dict -> [[AST_Node], [str]]
    def c_main(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_Program)):
            assembly = assembly + ["    b .main"] # add branch to the main of the program
            asts = asts[0].connections
        return (asts,assembly)
    
    # Compiles a begin block by adding its children to the front of the ast list
    # c_begin :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)
    def c_begin(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str], dict, dict]:
        if (isinstance(asts[0],AST_Begin)):
            asts = asts[0].connections + asts  # add connections to the ast list
        return (asts, assembly, labels, scope)
    
    # Compiles everything that can occur inside a code block. It currently can compile: expressions, if statements and function calls, if code blocks, variable declations
    # c_body :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)
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
    
    # This complex behemoth of a function compiles a function definition in pascal.
    # It will look forwards inside the function to see how many memory allocation is required. 
    # If this exceeds the amount of registers we have available we will switch to using the stack. 
    # This function fills the scope with functions that, will take a input or output register and store or load a variable in assembly.
    # These functions are dynamically generated based on how many other register/stack space has been used by previous variables.
    # # c_function_def :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)
    def c_function_def(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        
        # this function initializes the scope for all the upcoming named variables
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
            
        # this function initializes the scope for all the upcoming unnamed variables
        def c_expression(scope: dict, n: int, n_offset: int, i: int) -> Tuple[List[AST_Node], List[str]]:
            if n_offset + i >= n: 
                return scope
            if n <= 4:
                scope[str("E"+str(i))] = (lambda Rx: "    mov r"+str(n_offset+4+i)+", " + Rx, lambda Rx: "    mov " + Rx + ", r" + str(n_offset+4+i))
            else:
                scope[str("E"+str(i))] = (lambda Rx: "    str " + Rx + ", [r7,#"+str((n_offset+i)*4)+"]",       lambda Rx: "    ldr " + Rx + ", [r7,#"+str((n_offset+i)*4)+"]")
            return c_expression(scope, n, n_offset, i+1)
        
        
        if (isinstance(asts[0],AST_Function)):
            previous_scope = deepcopy(scope) # make a deepcopy of the current scope so we can restore it when we are done with generating assembly for inside the function.
            
            rslt_d:List[AST_Var] = self.get_declarations_nested(asts[0]) # number of var declarations ((nested) forward lookup)
            rslt_p = self.get_params(asts[0]) # number of parameters (forward lookup)
            
            n_d = len(rslt_d) # number of variable declarations
            n_p = len(rslt_p[0]) # number of parameters
            n_e = self.get_loads(asts[0]) # the maximum number of used registers (or stack space) simultaneous in use by expressions
            
            n = (n_d + n_p + n_e) # the number total used registers/stack space in this function
            
            rslt = "    push { r4"  if n else "    push { lr }"# push r4 for either first parameter or saving the stack pointer. If no register is in use only push lr
            tmp_rslt = [] # temporary variable for storing partially generated assembly
            
            
            # Here we safely store the parameters (r0,r1,r2,r3) using registers
            if n <= 4: # when using less then 4 variables we use registers
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
                rslt += ", ".join(["","r5","r6","r7"][:n]) # generates a str containing the used registers in this function. The amount is based off the how many registers we use. (expressed as n)
            
            rslt += ", lr }" if n else "" # closing the push instruction
            rslt = [rslt] + tmp_rslt # combining the assembly.
            
            # Here we safely store the parameters (r0,r1,r2,r3) using the stack
            if n > 4: # when using more then 4 variables we use the stack
                rslt = rslt + ["    sub sp, sp, #" + str(n*4)]
                rslt = rslt + ["    add r4, sp, #0"] # using add because sp does not support mov
                if n_p >= 1:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r4]",       lambda Rx: "    ldr   " + Rx + ", [r4]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r0")]
                if n_p >= 2:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r4, #4]",   lambda Rx: "    ldr   " + Rx + ", [r4, #4]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r1")]
                if n_p >= 3:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r4, #8]",   lambda Rx: "    ldr   " + Rx + ", [r4, #8]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r2")]
                if n_p >= 4:
                    scope[rslt_p[0][0].parameter_name] = (lambda Rx: "    str " + Rx + ", [r4, #12]",  lambda Rx: "    ldr   " + Rx + ", [r4, #12]")
                    rslt = rslt + [scope[rslt_p[0][0].parameter_name][0]("r3")]
            
            
            scope = c_vars(rslt_d,scope,n,n_p,n_e,0) # updating scope for the variables
            scope = c_expression(scope,n,n_p+n_d,0) # updating scope for the expression stores/loads when an operator has an operator for both children
            assembly = assembly + ["\n.global " + asts[0].procedure_name,asts[0].procedure_name + ":"] + rslt # prepend the procedure name and generating a .global to make it callable
            labels[asts[0].procedure_name] = (n_p, list(map(lambda x: str(x.type), rslt_p[0]))) # currently stores num of parameters labels and sets the label active also needs to store loops and if statements. loops, if statements or functions without parameters will contain 0 as num of parameters
            
            # this generated the closing pop instruction for the function. It also used the scope and pretends to be a variable. 
            # Since pascal returns using the same operater as setting a variable we can use the scope to generate each function return.
            scope[asts[0].procedure_name] = (lambda _: "    pop { " + ", ".join(["r4","r5","r6","r7"][:n if n <= 4 else 1]) + "".join([", ", "pc }"][int(not(n)):]) , lambda _: "return")
            # lastly we call the c_function_body compilerfunction to generate the assembly in the body using the initialized scope
            (_, assembly, labels, scope) = self.c_function_body(asts[0].connections, assembly, labels, scope)
            return (asts[1:], assembly, labels, previous_scope) # return the previous scope since we are outside our function
        return (asts, assembly, labels, scope) # we are not in a function definition
       
    # This function compiles function calls. It also generated code for getting the parameters in the right registers
    # c_function_call :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)    
    def c_function_call(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        if (isinstance(asts[0],AST_FunctionCall)):
            
            # 4 parameter
            if len(asts[0].connections) == 4:
                if len(asts[0][3].connections):
                    expr_assembly = self.c_expression([asts[0][3][0]], [], labels, scope) # expression inside function call for the parameter
                    assembly += expr_assembly[1] + ["    mov r3, r0"]      
                elif asts[0][3].type == "pvar":
                    assembly += [scope[str(asts[0][3].value)][1]("r3")] # variable
                else:
                    assembly += ["    mov r3, #" + str(asts[0][3].value)] # const value
            
            # 3 parameter
            if len(asts[0].connections) >= 3:
                if len(asts[0][2].connections):
                    expr_assembly = self.c_expression([asts[0][2][0]], [], labels, scope) # expression inside function call for the parameter
                    assembly += expr_assembly[1] + ["    mov r2, r0"]
                elif asts[0][2].type == "pvar":
                    assembly += [scope[str(asts[0][2].value)][1]("r2")]  # variable
                else:
                    assembly += ["    mov r2, #" + str(asts[0][2].value)] # const value
            
            # 2 parameter
            if len(asts[0].connections) >= 2:
                if len(asts[0][1].connections):
                    expr_assembly = self.c_expression([asts[0][1][0]], [], labels, scope)
                    assembly += expr_assembly[1] + ["    mov r1, r0"]
                elif asts[0][1].type == "pvar":
                    assembly += [scope[str(asts[0][1].value)][1]("r1")]
                else:
                    assembly += ["    mov r1, #" + str(asts[0][1].value)] # const value  
            
            # 1 parameter
            if len(asts[0].connections) >= 1:
                if len(asts[0][0].connections):
                    expr_assembly = self.c_expression([asts[0][0][0]], [], labels, scope)
                    assembly += expr_assembly[1]
                elif asts[0][0].type == "pvar":
                    assembly += [scope[str(asts[0][0].value)][1]("r0")]
                else:
                    assembly += ["    mov r0, #" + str(asts[0][0].value)] # const value
            return (asts[1:], assembly + ["    bl "+ asts[0]._function], labels, scope) # added bl to function and return
        return (asts, assembly, labels, scope)
            
    # This function compiles if statements
    # It generates 2 labels. One for the start of the false codeblock that runs when the evaluation of the if expression is false.
    # It also generates another label at the end of the if statement. 
    # When the the if expression is true, it does not take the branch ans just continues the code in the true codeblock.
    # At the end of the true codeblock it has a branch to the end of the if statement to not run the code inside the false codeblock.
    # c_if_statement :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)  
    def c_if_statement(self, asts:List[AST_Node], assembly:List[str], labels:dict, scope:dict) -> Tuple[List[AST_Node],List[str],dict,dict]:
        if isinstance(asts[0], AST_If):
            (label_start_false,labels) = self.generate_new_label(labels) # generate label for when expression is false
            (label_end_false,labels) = self.generate_new_label(labels)   # generate label for when we need to skip the false statement (at the end of the if_true block)
            # add expression evalation
            (_,assembly, labels, scope) = self.c_body((split_list_if(asts[0].connections, lambda x: isinstance(x, AST_Expression))[0]), assembly, labels, scope) # evaluate the expression
            assembly += ["    bne "+str(label_start_false[:-1])] # when the expression is false go to the start of the false block. If not continue inside the true block
            (_,assembly, labels, scope) = self.c_body((split_list_if(asts[0].connections, lambda x: isinstance(x, AST_IfTrue))[0]), assembly, labels, scope) # generate the true block
            assembly += ["    b "+str(label_end_false[:-1])] # branch to the end of the false block. We are outside the if block
            assembly += [label_start_false] # add the start of the start block 
            (_,assembly, labels, scope) = self.c_body((split_list_if(asts[0].connections, lambda x: isinstance(x, AST_IfFalse))[0]), assembly, labels, scope) # generates the false block
            assembly += [label_end_false] # add the end of the false block and thus the if statement
            return (asts[1:], assembly, labels, scope)
        return (asts, assembly, labels, scope)
    
    # This function compiles expressions.
    # **This function would have liked to have either pattern matching or switch statements**
    # Currently this function has quite a lot of cases and edge cases. 
    #
    # It follows a simple rule for calculation. It allocates r1 for the left side of an operator node and r2 for right side of an operator node.
    # When both left side and right side are operator nodes themselves, we store the intermediate value of r1 temporarily. 
    # Note: a function call is considered an operator themselves (even though they are a leaf node inside the expression tree)
    #
    # 
    # When both sides are const it tries to optimize. For example x := 4 * 4 could have been generated as such:
    # mov r1, #4 s
    # mov r2, #4
    # mul r1, r1, r2
    # mov x, r1
    # The optimizing code precalculates the value since both values are known at compile time and generates:
    # mov x, #16
    # 
    # When both side differ the side with the operator node becomes the new current_node
    # 
    # Our last instruction stores the instruction inside r0. We do this so it's easier to return 
    #
    # c_expression :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)  
    def c_expression(self, asts:List[AST_Node], assembly:List[str], labels: dict, scope: dict) -> Tuple[List[AST_Node], List[str]]:
        
        if (isinstance(asts[0],AST_Expression)): # check if we have an expression.
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
                        
                        # get the instruction and generate a part of the assembly and put it inside temp_assembly
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
                         
                        
                        # var and var
                        if current_node.left.type == "var" and current_node.right.type == "var": # both sides are vars
                            if return_register == "r0" and current_node.data == "*": # check if we use the mul operator and return register is r0
                                                                                     # we do this because mul r0, r1, r2 is invalid
                                return ([scope[current_node.left.data][1]("r1"),scope[current_node.right.data][1]("r2"),"    mul r1, r1, r2","    mov r0, r1"] + _assembly)
                            else:
                                return ([scope[current_node.left.data][1]("r1"),scope[current_node.right.data][1]("r2"),temp_assembly + "r1, r2"] + _assembly) # get both vars and add them inside the expression
                        
                        # var and const value
                        elif current_node.left.type == "var" and current_node.right.type not in ["func_call","var"] and isinstance(current_node.right, ExprLeaf) and current_node.data != "*":
                            return [scope[current_node.left.data][1]("r1"),temp_assembly + "r1, #" + str(current_node.right.data)] + _assembly
                        
                        # const value and var 
                        elif current_node.right.type == "var" and current_node.left.type not in ["func_call","var"] and isinstance(current_node.left, ExprLeaf):
                            return [scope[current_node.right.data][1]("r2"),"    mov r1, #" + str(current_node.left.data),temp_assembly + "r1, r2"] + _assembly
                        
                        # var and operator
                        elif isinstance(current_node.left, ExprLeaf) and current_node.left.type == "var":
                            if return_register == "r0" and current_node.data == "*":
                                _assembly = [scope[current_node.left.data][1]("r1"),"    mul r1, r1, r2","    mov r0, r1"] + _assembly # exception for r0 because mul r0, r1, r2 is invalid
                                return _c_expression(current_node.right,"r2",_assembly)
                            temp_assembly = temp_assembly + "r1"
                            _assembly = [scope[current_node.left.data][1]("r1"),temp_assembly] + _assembly
                            return _c_expression(current_node.right,"r2",_assembly)
                        
                        # operator and var
                        elif isinstance(current_node.right, ExprLeaf) and current_node.right.type == "var":
                            if return_register == "r0" and current_node.data == "*":
                                _assembly = [scope[current_node.right.data][1]("r2"),"    mul r1, r1, r2","    mov r0, r1"] + _assembly # exception for r0 because mul r0, r1, r2 is invalid
                                return _c_expression(current_node.left,"r1",_assembly)
                            temp_assembly = temp_assembly + "r1, r2"
                            _assembly = [scope[current_node.right.data][1]("r2"),temp_assembly] + _assembly
                            return _c_expression(current_node.left,"r1",_assembly)
                        
                        # funccall and operator
                        elif isinstance(current_node.left, ExprLeaf) and current_node.left.type == "func_call": # needs to call c_functioncall instead of scope
                            temp_assembly = temp_assembly + "r1, r2"
                            return [self.c_function_call([current_node.left],[],labels,scope)[1],scope["E"+str(current_node.e_value-1)][0]("r0")] + _c_expression(current_node.right,"r2",_assembly) + scope["E"+str(current_node.e_value-1)][1]("r1") + [temp_assembly] +  _assembly
                        
                        # operator and funccall
                        elif isinstance(current_node.right, ExprLeaf) and current_node.right.type == "func_call": # needs to call c_functioncall instead of scope
                            temp_assembly = temp_assembly + "r1, r2"
                            return [self.c_function_call([current_node.right],[],labels,scope)[1],scope["E"+str(current_node.e_value-1)][0]("r0")] + _c_expression(current_node.left,"r1",_assembly) + scope["E"+str(current_node.e_value-1)][1]("r2") + [temp_assembly] +  _assembly
                        
                        # const value and operator
                        elif isinstance(current_node.left, ExprLeaf) and current_node.left.type not in ["func_call","var"]  and current_node.data != "*": # left side is a const value
                            temp_assembly = temp_assembly + "r1, r2"
                            _assembly = [temp_assembly] + ["    mov r1, #" + str(current_node.left.data)] + _assembly
                            return _c_expression(current_node.right,"r2",_assembly)
                           
                        # operator and const value
                        elif isinstance(current_node.right, ExprLeaf) and current_node.right.type not in ["func_call","var"]  and current_node.data != "*":
                            temp_assembly = temp_assembly + "r1, #" + str(current_node.right.data)
                            _assembly = [temp_assembly] + _assembly
                            return _c_expression(current_node.left,"r1",_assembly)
                        
                        # operator * and const value. This will input a const value inside the expression function thus failing exprnode check and generating the mov instruction
                        elif current_node.data == "*" and current_node.right.type not in ["func_call","var"]:
                            temp_assembly = temp_assembly + "r1, r2"
                            _assembly = [temp_assembly] + _assembly
                            return _c_expression(current_node.right,"r2",_assembly)
                        
                        else:
                            # since _assembly is build by inserting new assembly lines in the front it is easier to read this code from the end to the beginning..
                            
                            # generates operator instruction 
                            _assembly = [temp_assembly + ("r1, r2" if current_node.left.type != "func_call" else "r0, r2")] + _assembly # use r0 if funccall was used in right side
                            # load from stack / register
                            _assembly = [scope["E"+str(current_node.e_value-1)][1]("r2")] + _assembly # restore result right side
                            
                            
                            if current_node.left.type != "func_call":
                                _assembly = _c_expression(current_node.left, "r1", _assembly) # generate left side
                            else:
                                _assembly = self.c_function_call([current_node.left], [], labels, scope)[1] + _assembly # execute left function 
                            
                            # store to stack / register
                            _assembly = [scope["E"+str(current_node.e_value-1)][0]("r2" if current_node.right.type != "func_call" else "r0")] + _assembly # safely store result of right side
                            
                            if current_node.right.type != "func_call":
                                _assembly = _c_expression(current_node.right, "r2", _assembly) # generate right side
                            else:
                                _assembly = self.c_function_call([current_node.right], [], labels, scope)[1] + _assembly # function call of right side
                                
                            return _assembly
                        
                # Generate mov instruction of const value to return register.
                # Used to generate mul instruction since it doesn't support const value.
                # Since mul r1, #3 is not allowed.
                elif isinstance(current_node, ExprLeaf) and current_node.type != ["func_call","var"]:
                    return ["    mov " + str(return_register) + ", #" + str(current_node.data)] + _assembly  
                        
                else:
                    assert("Invalid expression")
                    
            top_node = asts[0].right # The highest node and thus the node that needs to be executed last.
            if (isinstance(top_node, ExprNode)):
                
                # top_node is assignment
                if top_node.data == ":=": # assignment to var or function return
                    if isinstance(top_node.right, ExprLeaf): # simple assignment (x := 4) 
                        if scope[top_node.left.data][1]("") != "return": # check if we need to return this
                            assembly = assembly + [scope[top_node.left.data][0]("#" + str(top_node.right.data))] # just a variable
                        else: # function return
                            assembly = assembly + ["    mov r0, #" + str(top_node.right.data) , scope[top_node.left.data][0]("")] # Moving the const value to r0 and generate the pop instruction
                    else:
                        if isinstance(top_node.right, AST_FunctionCall): # function call no need to check for if this is a return statement since both generate valid pop instructions
                            assembly = assembly + self.c_function_call([top_node.right],[],labels,scope)[1] + [scope[top_node.left.data][0]("r0")]
                        else:
                            assembly = assembly + _c_expression(top_node.right,"r0",[]) + [scope[top_node.left.data][0]("r0")] # normal expression

                        
                    return (asts[1:],assembly,labels,scope)
                
                # top_node is comparison
                elif top_node.data == "=": # comparison 
                    temp_assembly = ""
                    
                    # simple comparison with 2 leaf nodes  
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
                            assembly += [self.c_function_call([top_node.left],[],labels,scope)[1]]
                            temp_assembly = "    cmp r1, r0"           
                        else:
                            temp_assembly += "#" + str(top_node.right.data)
                            
                    # right side is an expression
                    elif isinstance(top_node.left, ExprLeaf):
                        if top_node.left.type == "var":
                            assembly += _c_expression(top_node.right,"r2",[]) + [scope[top_node.left.data][1]("r1")]
                            temp_assembly = "    cmp r1, r2"
                        elif top_node.left.type == "func_call":
                            assembly += _c_expression(top_node.right,"r2",[]) + [scope["E"+str(top_node.e_value-1)][0]("r2"),self.c_function_call(top_node.right,[],labels,scope)[1],scope["E"+str(top_node.e_value-1)][0]("r2")]
                            temp_assembly = "    cmp r0, r2"
                        else:
                            assembly += _c_expression(top_node.right,"r1",[])
                            assembly += ["    cmp r1, #" + str(top_node.left.data)]
                            
                    # left side is an expression
                    elif isinstance(top_node.right, ExprLeaf):
                        if top_node.right.type == "var":
                            assembly += _c_expression(top_node.left,"r2",[]) + [scope[top_node.right.data][1]("r1")]
                            temp_assembly = "    cmp r1, r2"
                        elif top_node.left.type == "func_call":
                            assembly += _c_expression(top_node.left,"r1",[]) + [scope["E"+str(top_node.e_value-1)][0]("r1"),self.c_function_call(top_node.right,[],labels,scope)[1],scope["E"+str(top_node.e_value-1)][0]("r1")]
                            temp_assembly = "    cmp r1, r0"
                        else:
                            temp_assembly += "    cmp r1, #" + str(top_node.right.data)
                            assembly += _c_expression(top_node.left,"r1",[])
                    # both sides are an experssion
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
                return (asts[1:], assembly, labels, scope) # useless expression we don't need to generate any assembly for this since it does not change anything. Example of an useless expression is: (5)
        return (asts, assembly, labels, scope)
    
    # simple parses a body block. Moves the children connections into the ast list and removes itself
    # c_function_body :: [AST_Node] -> [str] -> dict -> dict -> (AST_Node, [str], dict, dict)  
    def c_function_body(self, asts:List[AST_Node], assembly:List[str], labels:dict, scope:dict) -> Tuple[List[AST_Node],List[str],dict,dict]:
        (body, _) = self.get_body(asts)
        if isinstance(body[0], AST_Begin):
            connections:AST_Node = body[0].connections
            return self.c_body(connections, assembly, labels, scope)
        else:
            assert("No body found in function")
        return ([], assembly, labels, scope)
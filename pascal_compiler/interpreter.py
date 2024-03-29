from utils import *

# CLASS : Var
# Brief : This class stores a variable, used as a struct
class Var:
    def __init__(self, var_name: str, var_type: str, value: Union[int,str,bool,None]):
        self.var_name = var_name
        self.type = var_type
        self.value: Union[int,str,bool,None] = value

    def __str__(self) -> str:
        return str(self.value)
    
    __repr__ = __str__


# CLASS : Functions
# Brief : This class implements a dict to store functions 
# Functions:
# add_function : this function adds a function to the internal dict
# get_function : this function gets a function from the internal dict, return a list of ast_nodes
class Functions:
    def __init__(self):
        self.functions = {}
    
    # add_function :: Functions -> str -> [AST_Node] -> Functions
    def add_function(self, function_name: str, instructions: List[AST_Node]):
        self.functions[function_name] = instructions
        return self
    
    # get_function :: Functions -> str -> [AST_Node]
    def get_function(self, function_name: str) -> List[AST_Node]:
        if function_name in self.functions:
            return self.functions[function_name]
        raise Exception('Undefined function ' + function_name)
    
    def __str__(self) -> str:
        return str(self.functions)
    
    __repr__ = __str__

# CLASS : Interpreter
# Brief : This class runs the ast
#
# Functions:
# add_lib : adds other functions from other files
# get_functions : internal function used to get all function from the ast
# get_globals : internal function used to get all global declared variables from the ast
# readLn : internal function to get the input from the user
# run : runs the ast
# runner : internal function to run the ast. Checks for if,repeat,expressions,var declarations, function calls etc
# function_call : internal function to handle functioncall in pascall
#
# variables: 
# self.functions : stores all functions 
# self.globals : stores all globals
# self.variables : stores variables
# self.ast : stores a list of the current execution stack
#
# note: all internal used variables start with . (for example return variables)
class Interpreter:
    def __init__(self, ast: AST_Program):
        self.functions = Functions() # wrapper around a dict
        (funcs, self.ast) = self.get_functions(ast)
        self.functions = list(map(lambda func: self.functions.add_function(func.procedure_name,func.connections), funcs))[-1]
        (globals, self.ast) = self.get_globals(self.ast)
        self.globals = dict(list(map(lambda _global: (_global.var_name, (_global.var_type, None)),globals)))
        self.variables = [{}] 
        self.variables[-1] = set_var(Var('.return','integer',None),self.variables[-1])
    
    # add_lib :: [AST_Node] -> Interpreter
    def add_lib(self, ast):
        (funcs, _) = self.get_functions(ast)
        self.functions = list(map(lambda func: self.functions.add_function(func.procedure_name,func.connections), funcs))[-1]
        return self
    
    # get_functions :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_functions(self, asts:List[AST_Node]) -> Tuple[List[AST_Node]]:
        return split_list_if(asts, lambda x: isinstance(x, AST_Function))
    
    # get_globals :: [AST_Node] -> ([AST_Node],[AST_Node])
    def get_globals(self, asts:List[AST_Node]):
        return split_list_if(asts, lambda x: isinstance(x, AST_Var))
    
    # readln :: int | str
    def readln(self) -> Union[int,str]:
        input_data = input()
        if input_data.isdigit():
            return int(input_data)
        else:
            return str(input_data)
    
    # run :: (dict,dict)
    def run(self) -> Tuple[dict,dict]:
        return self.runner(self.ast)
    
    # runner :: AST_Node -> (dict,dict)
    def runner(self, ast: AST_Node) -> Tuple[dict,dict]:
        def evaluate_expression(node: Union[ExprLeaf,ExprNode,AST_FunctionCall,AST_ReadLn]) -> Union[None,int,str,bool]:
            ## LEAF
            
            if isinstance(node, ExprLeaf):
                if node.type == 'var':
                    rslt = get_var(node.data,self.variables[-1],self.globals)
                    if rslt[0] == 'integer' or isinstance(rslt[1], int) or rslt[1].isdigit():
                        return int(rslt[1])
                    return rslt[1]
                else:
                    if node.type == 'digit':
                        return int(node.data)
                    if node.type == 'string':
                        return str(node.data)            
            
            ## Function call (leaf)
            if isinstance(node, AST_FunctionCall):
                (function_ast,self.variables) = self.function_call(node._function,[node],self.variables)
                (self.variables, self.globals) = self.runner(function_ast)
                return get_var('.return',self.variables[-1],self.globals)[1]
            
            ## ReadLn call (leaf)
            if isinstance(node, AST_ReadLn):
                return self.readln()
            
            ## OPERATORS
            if node.data == '+':
                return evaluate_expression(node.left) + evaluate_expression(node.right)
            if node.data == '-':
                return evaluate_expression(node.left) - evaluate_expression(node.right)
            if node.data == ':=':
                data = (get_var(node.left.data,self.variables[-1],self.globals)[0],evaluate_expression(node.right))
                self.variables[-1] = set_var(Var(node.left.data,*data),self.variables[-1])
                self.variables[-1] = set_var(Var('.return',*data),self.variables[-1]) # also setting the return value if because this assignment could be the last call of the function call
                return None # no need to set the .return again so we return None
            if node.data == '*':
                return evaluate_expression(node.left) * evaluate_expression(node.right)
            if node.data == '/':
                return evaluate_expression(node.left) / evaluate_expression(node.right)
            if node.data == 'or':
                return bool(evaluate_expression(node.left)) or bool(evaluate_expression(node.right))
            if node.data == 'and':
                return bool(evaluate_expression(node.left)) and bool(evaluate_expression(node.right))
            if node.data == '=':
                return evaluate_expression(node.left) == evaluate_expression(node.right)
            if node.data == '<':
                return evaluate_expression(node.left) < evaluate_expression(node.right)
            if node.data == '>':
                return evaluate_expression(node.left) > evaluate_expression(node.right)
            if node.data == '>=':
                return evaluate_expression(node.left) >= evaluate_expression(node.right)
            if node.data == '<=':
                return evaluate_expression(node.left) <= evaluate_expression(node.right)
            
        if ast:        
            if isinstance(ast[0], AST_Begin):
                ast = ast[0].connections + ast[1:]
                return self.runner(ast)
            
            elif isinstance(ast[0], AST_Expression):
                if ast[0].right:  
                    eval = evaluate_expression(ast[0].right)
                    if isinstance(eval,int):
                        self.variables[-1] = set_var(Var('.return','integer',eval),self.variables[-1]) # sets return value to the evaluated value and returns it as int
                    if isinstance(eval,str):
                        self.variables[-1] = set_var(Var('.return','string',eval),self.variables[-1]) # sets return value to the evaluated value and returns it as string
                    if isinstance(eval,bool):
                        self.variables[-1] = set_var(Var('.return','bool',eval),self.variables[-1]) # sets return value to the evaluated value and returns it as bool
                    ast = ast[1:]
                    return self.runner(ast)
                else:
                    raise Exception('Error in expression')
                
            elif isinstance(ast[0], AST_FunctionCall):
                (ast,self.variables) = self.function_call(ast[0]._function,ast,self.variables)
                
                return self.runner(ast)
            elif isinstance(ast[0], AST_WriteLn):
                print(functools.reduce((lambda rslt, param_print: (rslt + ( (str(get_var(param_print.value,self.variables[-1],self.globals)[1])) if param_print._type == 'identifier' else (str(param_print.value)) if param_print._type != 'expression' else str(evaluate_expression(param_print.connections[0].right))))),ast[0].connections, ""))
                ast = ast[1:]
                self.variables[-1] = set_var(Var('.return','integer',None),self.variables[-1]) # sets return value to None
                return self.runner(ast)
            
            elif isinstance(ast[0], AST_ReadLn):
                ast = ast[1:]
                self.variables[-1] = set_var(self.readln(),self.variables[-1])
                return self.runner(ast)
            
            elif isinstance(ast[0], AST_Var):
                self.variables[-1] = set_var(Var('.return','integer',None),self.variables[-1]) # sets return value to None
                self.variables[-1] = set_var(Var(ast[0].var_name,ast[0].var_type,None),self.variables[-1]) # Made a variable with no value yet
                ast = ast[1:]
                return self.runner(ast)
            
            elif isinstance(ast[0], AST_EndFunctionCall):
                ast = ast[1:]
                self.variables[-2] = set_var(Var('.return',*get_var('.return',self.variables[-1],self.globals)),self.variables[-2]) # pass the return statement
                self.variables = self.variables[:-1] # remove the current scope since we are existing the function call
                return self.runner(ast)
            
            elif(isinstance(ast[0], AST_If)):
                if(evaluate_expression(ast[0].connections[0].right)): ## check the result of the if statement
                    ast = ast[0].connections[1].connections + ast[1:] ## if true block
                elif(len(ast[0].connections) > 2):
                    ast = ast[0].connections[2].connections + ast[1:] ## if false block
                else:
                    ast = ast[1:] # if false block does not exist
                return self.runner(ast)
            
            elif(isinstance(ast[0], AST_Repeat)):
                (self.variables, self.globals) = self.runner(ast[0].connections) # giving only the the ast inside the repeat block
                if bool(get_var('.return',self.variables[-1],self.globals)[1]): # check the result of the until statement
                    return self.runner(ast[1:]) # we are done repeating
                return self.runner(ast) # we are not done repeating yet
            
            raise Exception("This is not implemented in the interpreter! - ", ast[0])
        return (self.variables, self.globals)
            
    # function_call :: str -> [AST_Node] -> [dict] -> ([AST_Node],[dict])
    def function_call(self, function_name: str, ast: List[AST_Node], vars: List[dict]) -> Tuple[List[AST_Node],List[dict]]:
        _args  = set_var(Var('.return','integer',None),{} ) # args passed down to the function
        _fcall = ast[0] # function call ast node to store to get the args to be passed down
        ast[0] = AST_EndFunctionCall()
        ast = self.functions.get_function(function_name) + ast # prepend the function implementation to list of asts
        def create_arg(arg:AST_Parameter, arg_name: str):
            if arg._type == 'identifier':
                return Var(arg_name, *get_var(arg.value,vars[-1],self.globals)) # get the var from the scope provided with the function_call (this is a where clause on a function language) * we don't modify the any of the parameters
            if arg._type == 'digit':
                return Var(arg_name, 'integer' ,arg.value) # return a var as digit
            if arg._type == 'expression':
                (self.variables, self.globals) = self.runner([arg.connections[0]])
                return Var(arg_name,*get_var('.return',self.variables[-1],self.globals)) # call the expression
            if arg._type == 'string':
                return Var(arg_name, 'string' ,arg.value) # return a var as string
            raise Exception('No var could be created')
        
        (_params, ast) = split_list_if(ast, lambda x: isinstance(x, AST_FunctionParameter)) # splitting the params of the code block
        (return_type, ast) = split_list_if(ast, lambda x: isinstance(x, AST_FunctionReturnType)) 
        if return_type:
            _args  = set_var(Var('.return',return_type[0].return_type,None),_args )
            _args =  set_var(Var(function_name,return_type[0].return_type,None),_args )
        args_vars = list(map(lambda arg, param: create_arg(arg, param.parameter_name), _fcall.connections,_params)) # creating the new variables for inside the function call
        _args = functools.reduce(lambda scope,var: set_var(var,scope), args_vars,_args) # adding them to a lookup dictionary
        vars.append(_args) # appending dictionary to the top of the "stack"
        return (ast,vars) # returning the modified data

# get_var :: str -> dict -> dict -> (str,A)
def get_var(var_name: str, local_scope:dict, globals:dict) -> Tuple[str,A]:
    if var_name in local_scope: # first try and find the variable inside the local scope
        return local_scope[var_name]
    if var_name in globals: # variable not fount in the local scope. Lets try and find it in the global scope
        return globals[var_name]
    raise Exception('Variable not initialized or out of scope: ' + var_name) # variable does not exist

# set_var :: Var -> dict -> dict
def set_var(var: Var, scope: dict) -> dict:
    if isinstance(var.value,Var):
        raise Exception('Got a variable inside a variable')
    if var.value == None:
        vv = var.value
    elif var.type == 'string':
        vv = str(var.value)
    elif var.type == 'integer' or isinstance(var.value,int) or var.value.isdigit():
        vv = int(var.value)
    else:
        vv = str(var.value)
    scope[var.var_name] = (var.type, vv) 
    return scope
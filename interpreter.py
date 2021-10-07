from utils import *

class Var:
    def __init__(self, var_name, var_type, value):
        self.var_name = var_name
        self.type = var_type
        self.value = value
        
    def __str__(self):
        return str(self.value)
    
    __repr__ = __str__

class Functions:
    def __init__(self):
        self.functions = {}
        
    def add_function(self, function_name, instructions):
        self.functions[function_name] = instructions
        return self
        
    def get_function(self, function_name):
        if function_name in self.functions:
            return self.functions[function_name]
        raise Exception('Undefined function' + function_name)
    
    def __str__(self):
        return str(self.functions)
    
    __repr__ = __str__


## all internal used variables start with .

class Interpreter:
    def __init__(self, ast):
        self.functions = Functions() # wrapper around a dict
        (funcs, self.ast) = self.get_functions(ast)
        self.functions = list(map(lambda func: self.functions.add_function(func.procedure_name,func.connections), funcs))[-1]
        (globals, self.ast) = self.get_globals(self.ast)
        self.globals = dict(list(map(lambda _global: (_global.var_name, (_global.var_type, None)),globals)))
        self.variables = [{}] 
        self.variables[-1] = set_var(Var('.return','integer',None),self.variables[-1])
    
    def get_functions(self, asts:List[AST_Node]):
        return split_list_if(asts, lambda x: isinstance(x, AST_Function))
    
    def get_globals(self, asts:List[AST_Node]):
        return split_list_if(asts, lambda x: isinstance(x, AST_Var))
        
    def readln(self):
        input_data = input()
        if input_data.isdigit():
            return Var('.return','int',int(input_data))
        else:
            return Var('.return','str',str(input_data))
    def run(self):
        return self.runner(self.ast)
    def runner(self, ast):
        if ast:
            if isinstance(ast[0], AST_Begin):
                ast = ast[0].connections + ast[1:]
                return self.runner(ast)
            elif isinstance(ast[0], AST_Expression):
                if ast[0].right:
                    def evaluate_expression(node):
                        ## LEAF
                        if isinstance(node, ExprLeaf):
                            return node.data
                        
                        ## Function call (leaf)
                        if isinstance(node, AST_FunctionCall):
                            (_,self.variables) = self.function_call(node._function,[node],self.variables)
                            return get_var('.return',self.variables,self.globals)[1]
                        
                        ## ReadLn call (leaf)
                        if isinstance(node, AST_ReadLn):
                            return self.readln()
                        
                        ## OPERATORS
                        if node.data == '+':
                            return evaluate_expression(node.left) + evaluate_expression(node.right)
                        if node.data == '-':
                            return evaluate_expression(node.left) - evaluate_expression(node.right)
                        if node.data == ':=':
                            self.variables[-1] = set_var(Var(node.left.data,get_var(node.left.data,self.variables[-1],self.globals)[0],evaluate_expression(node.right)),self.variables[-1])
                            return None
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
                        
                    eval = evaluate_expression(ast[0].right)
                    if isinstance(eval,int):
                        self.variables[-1] = set_var(Var('.return','integer',eval),self.variables[-1],) # sets return value to the evaluated value and returns it as int
                    if isinstance(eval,str):
                        self.variables[-1] = set_var(Var('.return','string',eval),self.variables[-1],) # sets return value to the evaluated value and returns it as string
                    ast = ast[1:]
                    return self.runner(ast)
                else:
                    raise Exception('Error in expression')
            elif isinstance(ast[0], AST_FunctionCall):
                (ast,self.variables) = self.function_call(ast[0]._function,ast,self.variables)
                return self.runner(ast)
            elif isinstance(ast[0], AST_WriteLn):
                print(functools.reduce((lambda rslt, param_print: (rslt + ((str(param_print.value)) if param_print._type != 'identifier' else str(get_var(param_print.value,self.variables[-1],self.globals)[1])))),ast[0].connections, ""))
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
            elif isinstance(ast[0], AST_Var):
                self.variables[-1] = set_var(Var('.return','integer',None),self.variables[-1],) # sets return value to None
                self.variables[-1] = set_var(Var(ast[0].var_name,ast[0].var_type,None),self.variables[-1]) # Made a variable with no value yet
                ast = ast[1:]
                return self.runner(ast)
            elif isinstance(ast[0], AST_EndFunctionCall):
                ast = ast[1:]
                self.variables[-2] = set_var(Var('.return',*get_var('.return',self.variables[-1],self.globals)),self.variables[-2]) # pass the return statement
                self.variables = self.variables[:-1] # remove the current scope since we are existing the function call
                return self.runner(ast)
        return (self.variables, self.globals)
            
                
    def function_call(self, function_name: str, ast: List[AST_Node], vars: List[dict]):
        
        _args  = set_var(Var('.return','integer',None),{} ) # args passed down to the function
        _fcall = ast[0] # function call ast node to store to get the args to be passed down
        ast[0] = AST_EndFunctionCall()
        ast = self.functions.get_function(function_name) + ast # prepend the function implementation to list of asts
        def create_arg(arg:AST_Parameter, arg_name: str):
            if arg._type == 'identifier':
                return Var(arg_name, *get_var(arg.value,vars[-1],self.globals)) # get the var from the scope provided with the function_call (this is a where clause on a function language) * we dont modify the any of the parameters
            if arg._type == 'digit':
                return Var(arg_name, 'integer' ,arg.value) # return a var as digit
            if arg._type == 'string':
                return Var(arg_name, 'string' ,arg.value) # return a var as string
            if arg._type == 'expression':
                (self.variables, self.globals) = self.runner([arg])
                return Var(arg_name,*get_var('.return',self.variables[-1],self.globals)) # call the expression
        
        (_params, ast) = split_list_if(ast, lambda x: isinstance(x, AST_FunctionParameter)) # splitting the params of the code block
        args_vars = list(map(lambda arg, param: create_arg(arg, param.parameter_name), _fcall.connections,_params)) # creating the new variables for inside the function call
        _args = functools.reduce(lambda scope,var: set_var(var,scope), args_vars,_args) # adding them to a lookup dictonary
        vars.append(_args) # appending dictorary to the top of the "stack"
        return (ast,vars) # returning the modified data
        
def split_list_if(lst:List[A], condition: Callable[[A],bool]) -> Tuple[List[A],List[A]]:
        return (list(filter(condition,lst)),list(filter(lambda x: not condition(x),lst))) # splitting a list into a tuple containing two lists. the first list in the tuple holds all items where the condition holds true, the remaining items are second list inside the tuple.
               
def get_var(var_name, local_scope, globals):
    if var_name in local_scope: # first try and find the variable inside the local scope
        return local_scope[var_name]
    if var_name in globals: # variable not fount in the local scope. Lets try and find it in the global scope
        return globals[var_name]
    raise Exception('Variable not initialized or out of scope: ' + var_name) # variable does not exist

def set_var(var: Var, scope):
    scope[var.var_name] = (var.type, var.value) # might be abled to set a undeclared variable
    return scope




        
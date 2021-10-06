from utils import *

class Var:
    def __init__(self, var_name, var_type, value):
        self.var_name = var_name
        self.type = var_type
        self.value = value
        
    def __str__(self):
        return str(self.var_name) + ',' + str(self.type) +  ',' + str(self.value)
    
    __repr__ = __str__
        
class Stack:
    def __init__(self):
        self.stack = []
    def push(self, item):
        self.stack.append(item)
        return (self,item)
    def pop(self):
        return (self,self.stack.pop())
    def size(self):
        return len(self.stack)
    
    def __str__(self):
        return str(self.stack)
    
    __repr__ = __str__

class Functions:
    def __init__(self):
        self.functions = {}
        
    def add_function(self, function_name, instructions):
        self.functions[function_name] = instructions
        return self
        
    def get_function(self, function_name):
        return self.functions[function_name]
    
    def __str__(self):
        return str(self.functions)
    
    __repr__ = __str__


class Interpreter:
    def __init__(self, ast):
        self.functions = Functions() # wrapper around a dict
        (funcs, self.ast) = self.get_functions(ast)
        self.functions = list(map(lambda func: self.functions.add_function(func.procedure_name,func.connections), funcs))[-1]
        (globals, self.ast) = self.get_globals(self.ast)
        self.globals = dict(list(map(lambda _global: (_global.var_name, (_global.var_type, None)),globals)))
        self.args = {}
        self.variables = [{}]
        print(self.ast)
        
    def split_list_if(self, lst, condition):
        return (list(filter(condition,lst)),list(filter(lambda x: not condition(x),lst)))
    
    def get_functions(self, asts:List[AST_Node]):
        return self.split_list_if(asts, lambda x: isinstance(x, AST_Function))
    
    def get_globals(self, asts:List[AST_Node]):
        return self.split_list_if(asts, lambda x: isinstance(x, AST_Var))
    
def get_var(var_name, local_scope, args, globals):
    if var_name in local_scope:
        return local_scope[var_name]
    if var_name in args:
        return args[var_name]
    if var_name in globals:
        return globals[var_name]
    raise Exception('Variable not initialized or out of scope')

def set_var(var: Var, scope):
    scope[var.var_name] = (var.var_type, var.value)
    return scope

    
class ProgramState:
    def __init__(self):
        self.stack = Stack()
        self.stack.push([])
        
    def add_variable(self, var):
        self.stack.stack[0]
        return self
    


        
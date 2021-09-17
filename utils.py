import functools
from typing import List, Tuple, Callable
from pathlib import Path

def compose(functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

# CLASS : Token
# Brief : This class stores tokens that are generated from the lexer and used in the parser class
# Descr : The class stores 2 values: name & data. name is used for the tokenname. data is used for the exctual data. 
# For example; name: keyword value: var
class Token:
    def __init__(self, name, data = ''):
        self.name = name
        self.data = data
        
    def __str__(self):
        return '(' + self.name + ',' + self.data + ') '
        
    def __eq__(self, other):
        return check_token_equal_all(self,other) or ((check_token_equal_name(self,other) and (self.data == '' or other.data == '')))
    
    __repr__ = __str__
    
# check_token_equal_name :: Token -> Token -> Bool
def check_token_equal_name(token1: Token,token2: Token) -> bool:
    return token1.name == token2.name

# check_token_equal_data :: Token -> Token -> Bool
def check_token_equal_data(token1: Token,token2: Token) -> bool:
    return token1.data == token2.data

# check_token_equal_all :: Token -> Token -> Bool
def check_token_equal_all(token1: Token,token2: Token) -> bool:
    return check_token_equal_data(token1,token2) and check_token_equal_name(token1,token2)

# CLASS : AST_Node
# Brief : This class stores nodes that are generated from the parser and used in the interpreter class for executing the pascal program
# Descr : The class stores 2 values: type & connections. type is used for the current node type. connection is used for storing underlying nodes. This class is accesible with [] operator.
# This class is the main class which all AST_Node derivatives inhereted from. Child classes are used to store more data and differentiate between AST types
class AST_Node:
    def __init__(self, ast_type, connections = []):
        self.type = ast_type
        self.connections = connections
        
    def set_connections(self, connections):
        self.connections = connections
        
    def get_connections(self):
        return self.connections
    
    def get_type(self):
        return self.type
    
    def set_type(self, new_type):
        self.type = new_type
    
    def __getitem__(self, key):
        return self.connections[key]
    
    def __setitem__(self, key, node):
        self.connections[key] = node
        
    def __delitem__(self, key):
        del self.connections[key]
        
    def append(self, node):
        self.connections.append(node)
        
    def __str__(self, level=0):
        ret = "-"*level+repr(self.type)+"\n"
        for connection in self.connections:
            ret += connection.__str__(level+1)
        return ret
    
    __repr__ = __str__
    
class AST_ERROR(AST_Node):
    def __init__(self, connections, program_name):
        super().__init__("error",[connections])
        self.program_name = program_name


class AST_Program(AST_Node):
    def __init__(self, ast_type, connections, program_name):
        super().__init__(ast_type,connections)
        self.program_name = program_name

class AST_Function(AST_Node):
    def __init__(self, ast_type, connections, procedure_name):
        super().__init__(ast_type,connections)
        self.procedure_name = procedure_name
        
class AST_Begin(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
      
class AST_FunctionParameter(AST_Node):
    def __init__(self, ast_type, connections, parameter_name, parameter_type):
        super().__init__(ast_type,connections)
        self.parameter_name = parameter_name
        self.parameter_type = parameter_type

class AST_Parameter(AST_Node):
    def __init__(self, ast_type, connections, value, _type):
        super().__init__(ast_type,connections)
        self.value = value
        self._type = _type

class AST_FunctionReturnType(AST_Node):
    def __init__(self, ast_type, connections, return_type):
        super().__init__(ast_type,connections)
        self.return_type = return_type
        
class AST_Var(AST_Node):
    def __init__(self, ast_type, connections, var_name, var_type):
        super().__init__(ast_type,connections)
        self.procedure_name = var_name
        self.return_type = var_type
        
class AST_Block(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
        
class AST_Repeat(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
        
class AST_RepeatBlock(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
        
class AST_If(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
        
class AST_IfTrue(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)

    
class AST_IfFalse(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
        
class AST_WriteLn(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)

        
# pre_prossesing :: String -> String
def pre_prossesing(program: str) -> str:
    program = program.replace('\n', '')
    program = program.replace('\t', '    ')
    return program

#Should probably be included in the parser and using the corrosponding token instead of string
class OperatorPrecedance:
    def __init__(self):
        self.op = [('<=',1),('>=',1),('=',1), (':=',0), ('::=',0), (':',1), ('<',1), ('>',1), ('+',2), ('-',2), ('*',3), ('/',3), ('(',4), (')',4)]
        

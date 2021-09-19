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
        if data == '':
            self.data = self.name
    def __str__(self):
        return '(' + self.name + ',' + self.data + ') '
        
    def __eq__(self, other):
        return check_token_equal_all(self,other) or ((check_token_equal_name(self,other) and (self.data == self.name or other.data == other.name)))
    
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

class AST_Expression(AST_Node):
    def __init__(self, ast_type, connections):
        super().__init__(ast_type,connections)
        self.expression = None
        
class AST_ExpressionAssignment(AST_Node):
    def __init__(self, ast_type, connections, var_name):
        super().__init__(ast_type,connections)
        self.var = var_name
        
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

class AST_Temp(AST_Node):
    def __init__(self):
        super().__init__('temp',[])


# pre_prossesing :: String -> String
def pre_prossesing(program: str) -> str:
    program = program.replace('\n', '')
    program = program.replace('\t', '    ')
    return program

class ExprNode(AST_Node):
    def __init__(self, data, precedense):
        super().__init__("expression_node",[])
        self.data = data
        self.precedense = precedense
        self.left = None
        self.right = None
    
    def left(self, left = None):
        if left:
            self.left = left
            self.connections = []
            self.connections.append(self.left)
            if self.right:
                self.connections.append(self.right)
        return self.left
    
    def right(self, right = None):
        if right:
            self.right = right
            self.connections = []
            self.connections.append(self.left)
            self.connections.append(self.right)
        return self.right
    
    def __str__(self):
        return '(' + self.data + ') '
        
    def __eq__(self, other):
        return self.precedense == other.precedense
    
    def __lt__(self, other):
        return self.precedense < other.precedense
    
    def __gt__(self, other):
        return self.precedense > other.precedense
    
    __repr__ = __str__
    
class ExprLeaf(AST_Node):
    def __init__(self, type, data):
        super().__init__("expression_leaf",[])
        self.type = type #type or function or var
        self.data = data
        
    def __str__(self):
        return '(' + self.type + ',' + self.data + ') '
    
    __repr__ = __str__
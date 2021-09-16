from utils import *

class Parser():
    def __init__(self):
        self.orders =           {'program' :    (   [Token('keyword','program')   ,Token('identifier')      ,Token('keyword',';')], 
                                                    [check_token_equal_all        ,check_token_equal_name   ,check_token_equal_all]),
                                 'var_dec' :    (   [Token('keyword','var')       ,Token('identifier')      ,Token('operator',':')      , Token('type')             , Token('keyword',';')],
                                                    [check_token_equal_all        ,check_token_equal_name   ,check_token_equal_all      , check_token_equal_name    , check_token_equal_all]),                                     
                                 'func' :       (   [Token('keyword', 'function') ,Token('identifier')      ,Token('parentheses_open')],
                                                    [check_token_equal_all        ,check_token_equal_name   ,check_token_equal_name ]),
                                 'func_close':  (   [Token('parentheses_closed')  ,Token('keyword',';')],
                                                    [check_token_equal_name       ,check_token_equal_all]),
                                 'func_ret' :   (   [Token('parentheses_closed')  ,Token('operator',':')  ,Token('type')          ,  Token('keyword',';')],
                                                    [check_token_equal_name       ,check_token_equal_all  ,check_token_equal_name , check_token_equal_all]),
                                 'params'   :   (   [Token('keyword',',')   ,Token('identifier')    , Token('operator',':'), Token('type')],
                                                    [check_token_equal_all  ,check_token_equal_name , check_token_equal_all, check_token_equal_name]),
                                 'first_param' :(   [Token('identifier')    ,Token('operator',':')  , Token('type')],
                                                    [check_token_equal_name ,check_token_equal_all  , check_token_equal_name]),
                                 'begin' :      (   [Token('keyword','begin')],
                                                    [check_token_equal_all]),
                                 'repeat' :     (   [Token('keyword','repeat')],
                                                    [check_token_equal_all]),
                                 'var':         (   [Token('keyword','var')],
                                                    [check_token_equal_all]),
                                 'if' :         (   [Token('keyword','if')],
                                                    [Token('keyword','then')]),
                                 '()' :         (   [Token('parentheses_open')],
                                                    [Token('parentheses_closed')]),
                                 'if_true' :    (   [Token('keyword','then')],
                                                    [Token('keyword','else'), Token('keyword','end')]),
                                 'if_false' :   (   [Token('keyword','else')],
                                                    [Token('keyword',';')]),
                                 'until' :      (   [Token('keyword', 'until')],
                                                    [Token('keyword', ';')])
                                 
                                }
    # r_check :: [Token] -> [Token] -> [([Token] -> [Token] -> Bool)]
    def r_check(self, tokens: List[Token], expected_tokens: List[Token], checks: List[Callable[[[Token],[Token]], bool]]):
        if not len(checks):
            return True
        elif checks[0](tokens[0],expected_tokens[0]):
            return self.r_check(tokens[1:],expected_tokens[1:],checks[1:])
        return False
    
    def __str__(self):
        return 'Parses the output from the lexer'
    __repr__ = __str__    
    
    
    ## INIT PARSER ##
    
    # p_program :: [Token] -> AST_Node
    def p_program(self, tokens: List[Token]) -> AST_Node:
        if self.r_check(tokens, *(self.orders['program'])):   
            return self.p_function(((tokens[len(self.orders['program'][0]):]),AST_Program('program',[],tokens[1].name)))[1]
        else:
            print("No program identifier")
        return None

    
    ## START PARSERS ##
    
    # p_function :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_function(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['func'])):
            ast_function = AST_Function('function',[],data[0][1].name)
            data[1].append(ast_function)
            return (self.p_fu_function(((data[0][len(self.orders['func'][0]):]),ast_function))[0],data[1])
        else:
            return data
        
    # p_repeat :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_repeat(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['repeat'])):
            ast_repeat = AST_Repeat('repeat',[])
            data[1].append(ast_repeat)
            return (self.parse_nothing(((data[0][len(self.orders['repeat'][0]):]),ast_repeat))[0],data[1])
        else:
            return data
    
    # p_begin :: ([Token], AST_Node) -> ([Token], AST_Node) 
    def p_begin(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['begin'])):
            ast_begin = AST_Begin('begin',[])
            data[1].append(ast_begin)
            return (self.parse_nothing(((data[0][len(self.orders['begin'][0]):]),ast_begin))[0],data[1])
        else:
            return data
    
    # p_var :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_var(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['var'])):
            ast_var = AST_Var('var',[],data[0][1].name)
            data[1].append(ast_var)
            return (self.parse_nothing(((data[0][len(self.orders['var'][0]):]),ast_var))[0],data[1])
        else:
            return data
        
    # p_if :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_if(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if self.r_check(data[0], *(self.orders['if'])):
            ast_if = AST_If('if',[])
            data[1].append(ast_if)
            return (self.parse_nothing(((data[0][len(self.orders['if'][0]):]),ast_if))[0],data[1])
        else:
            return data
    
    # p_function_call :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_function_call(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        return data
    
    # p_writeLn :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_writeLn(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        return data
    
    # p_expression :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_expression(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        return data
    
    # p_undefined :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_undefined(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return data


    ## FOLLOW-UP PARSERS ##
    
    # p_fu_function :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_function(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_until_no_change(data, [self.p_function_param,self.p_function_first_param])
        if self.r_check(new_data[0], *(self.orders['func_close'])):
            new_data = self.p_function_def_closing(new_data)
            return self.p_begin(new_data) #function body
        elif self.r_check(new_data[0], *(self.orders['func_ret'])):
            new_data = self.p_function_def_closing_ret(new_data)
            return self.p_begin(new_data) #function body with return type
        else:
            print(new_data)
            print("ERROR IN FUNCTION DEFINITION")
            return ([],data[1])
        
    def p_fu_begin(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return self.parse_until_no_change(data, [self.p_if,self.p_var,self.p_writeLn,self.p_expression])
        
            
    ## CLOSING PARSERS ##
    
    # p_function_first_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_first_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['first_param'])):
            ast_param = AST_FunctionParameters('param',[])
            data[1].append(ast_param)
            return ((data[0][len(self.orders['first_param'][0]):]),data[1])
        return data
    
    # p_function_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['params'])):
            ast_param = AST_FunctionParameters('param',[])
            data[1].append(ast_param)
            return ((data[0][len(self.orders['params'][0]):]),data[1])
        return data
    
    # p_function_def_closing :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_def_closing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['func_close'])):
            return ((data[0][len(self.orders['func_close'][0]):]),data[1])
        return data
    
    # p_function_def_closing_ret :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_def_closing_ret(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['func_ret'])):
            ast_return = AST_FunctionReturnType('func_ret',[], data[0][2])
            data[1].append(ast_return)
            return ((data[0][len(self.orders['func_ret'][0]):]),data[1])
        return data
    
    
    ## PARSER HELPERS ##
    
    # parse_until_no_change :: ([Token], AST_Node) -> [(([Token],AST_Node) -> ([Token],AST_Node]))] -> ([Token], AST_Node)
    def parse_until_no_change(self, data: Tuple[List[Token],AST_Node], parsers: List[Callable[[Tuple[List[Token],AST_Node]],Tuple[List[Token],AST_Node]]]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_in_order_stop_at_succes(data, parsers)
        if not new_data[0] or len(data[0]) != len(new_data[0]):
            return new_data
        return self.parse_until_no_change(new_data, parsers)
    
    # parse_in_order :: ([Token], AST_Node) -> [(([Token],AST_Node) -> ([Token],AST_Node]))] -> ([Token], AST_Node)
    def parse_in_order(self, data: Tuple[List[Token],AST_Node], parsers: List[Callable[[Tuple[List[Token],AST_Node]],Tuple[List[Token],AST_Node]]]) -> Tuple[List[Token],AST_Node]:
        parsers.reverse()
        parserall = compose(parsers)
        return parserall(data)
    
    # parse_in_order :: ([Token], AST_Node) -> [(([Token],AST_Node) -> ([Token],AST_Node]))] -> ([Token], AST_Node)
    def parse_in_order_stop_at_succes(self, data: Tuple[List[Token],AST_Node], parsers: List[Callable[[Tuple[List[Token],AST_Node]],Tuple[List[Token],AST_Node]]]) -> Tuple[List[Token],AST_Node]:
        if not len(parsers):
            return data
        new_data = parsers[0](data)
        if not new_data[0] or len(data[0]) != len(new_data[0]):
            return new_data
        return self.parse_in_order_stop_at_succes(data,parsers[1:])

        
    ## WRAPPERS ##
    
    # run :: [Token] -> AST_Node
    def run(self, tokens):
        return self.p_program(tokens)
    
    
    ## DEBUG PARSERS ##

    def parse_nothing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        # temporary parser that parses nothing so to debug existing parsers :)
        return data
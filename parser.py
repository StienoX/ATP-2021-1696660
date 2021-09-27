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
                                 'func_ret' :   (   [Token('parentheses_closed')  ,Token('operator',':')    ,Token('type')              ,  Token('keyword',';')],
                                                    [check_token_equal_name       ,check_token_equal_all    ,check_token_equal_name     , check_token_equal_all]),
                                 'params'   :   (   [Token('keyword',',')         ,Token('identifier')      , Token('operator',':')     , Token('type')],
                                                    [check_token_equal_all        ,check_token_equal_name   , check_token_equal_all     , check_token_equal_name]),
                                 'first_param' :(   [Token('identifier')          ,Token('operator',':')    , Token('type')],
                                                    [check_token_equal_name       ,check_token_equal_all    , check_token_equal_name]),
                                 'begin' :      (   [Token('keyword','begin')],
                                                    [check_token_equal_all]),
                                 'repeat' :     (   [Token('keyword','repeat')],
                                                    [check_token_equal_all]),
                                 'var':         (   [Token('keyword','var')],
                                                    [check_token_equal_all]),
                                 'if' :         (   [Token('keyword','if')],
                                                    [check_token_equal_all]),
                                 'func_call':   (   [Token('identifier')          ,Token('parentheses_open')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'writeLn':     (   [Token('keyword','WriteLn')   ,Token('parentheses_open')],
                                                    [check_token_equal_all        ,check_token_equal_name]),
                                 'close':       (   [Token('parentheses_closed')],
                                                    [check_token_equal_name]),
                                 'open':        (   [Token('parentheses_open')],
                                                    [check_token_equal_name]),
                                 'semi':        (   [Token('keyword',';')],
                                                    [check_token_equal_all]),
                                 'end':         (   [Token('keyword','end')],
                                                    [check_token_equal_all]),
                                 'list':        (   [Token('keyword',',')         ,Token('identifier')],
                                                    [check_token_equal_all        ,check_token_equal_name]),
                                 'f_list':      (   [Token('identifier')],
                                                    [check_token_equal_name]),
                                 'str_list':    (   [Token('keyword',',')         ,Token('string')],
                                                    [check_token_equal_all        ,check_token_equal_name]),
                                 'str_f_list':  (   [Token('string')],
                                                    [check_token_equal_name]),
                                 'exp':         (   [Token('identifier')          ,Token('operator')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_2':       (   [Token('digit')               ,Token('operator')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_3':       (   [Token('string')              ,Token('operator')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_4':       (   [Token('identifier')          ,Token('parentheses_open')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_c':       (   [Token('identifier')          ,Token('parentheses_closed')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_2c':      (   [Token('digit')               ,Token('parentheses_closed')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_3c':      (   [Token('string')              ,Token('parentheses_closed')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'exp_s':       (   [Token('identifier')          ,Token('keyword',';')],
                                                    [check_token_equal_name       ,check_token_equal_all]),
                                 'exp_2s':      (   [Token('digit')               ,Token('keyword',';')],
                                                    [check_token_equal_name       ,check_token_equal_all]),
                                 'exp_3s':      (   [Token('string')              ,Token('keyword',';')],
                                                    [check_token_equal_name       ,check_token_equal_all]),
                                 'op':          (   [Token('operator')],
                                                    [check_token_equal_name])
                                 
                                }
        self.precedence_order = [(Token('operator','<='),1),
                                 (Token('operator','>='),1),
                                 (Token('operator','='),1), 
                                 (Token('operator',':='),0), 
                                 (Token('operator','::='),0), 
                                 (Token('operator',':'),1), 
                                 (Token('operator','<'),1), 
                                 (Token('operator','>'),1), 
                                 (Token('operator','+'),2), 
                                 (Token('operator','-'),2), 
                                 (Token('operator','*'),3), 
                                 (Token('operator','/'),3),
                                 (Token('operator','or'),0),
                                 (Token('operator','and'),0),
                                 ]
    
    # r_check :: [Token] -> [Token] -> [([Token] -> [Token] -> Bool)]
    def r_check(self, tokens: List[Token], expected_tokens: List[Token], checks: List[Callable[[[Token],[Token]], bool]]) -> bool:
        if not len(checks):
            return True
        elif len(tokens) and checks[0](tokens[0],expected_tokens[0]):
            return self.r_check(tokens[1:],expected_tokens[1:],checks[1:])
        return False

    def __str__(self):
        return 'Parses the output from the lexer'
    __repr__ = __str__
    
    def get_precedence(self, token: Token) -> int:
        def _get_precedence(po: List[Tuple[Token,int]]) -> int:  # in a functional language (haskell) this would have been a 'where'
            if len(po):
                if check_token_equal_all(token,po[0][0]):
                    return po[0][1]
                return _get_precedence(po[1:])
            return 9
        return _get_precedence(self.precedence_order)
    
    ## INIT PARSER ##
    
    # p_program :: [Token] -> AST_Node
    def p_program(self, tokens: List[Token]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(tokens, *(self.orders['program'])):   
            return self.parse_until_no_change(((tokens[len(self.orders['program'][0]):]),AST_Program('program',[],tokens[1].name)), 
                                              [self.p_function,self.p_if,self.p_var,self.p_writeLn,self.p_expression])
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
            return self.parse_in_order((self.p_fu_begin(((data[0][len(self.orders['begin'][0]):]),ast_begin))[0],data[1]), [self.p_end, self.p_semicolomn])
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
            return (self.p_fu_if(((data[0][len(self.orders['if'][0]):]),ast_if))[0],data[1])
        else:
            return data
    
    # p_function_call :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_function_call(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:  
        if self.r_check(data[0], *(self.orders['writeLn'])):
            ast_writeLn = AST_WriteLn('writeLn', [])
            data[1].append(ast_writeLn)
            return (self.p_fu_function_call(((data[0][len(self.orders['writeLn'][0]):]),ast_writeLn))[0],data[1])
            
        return data
    
    # p_writeLn :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_writeLn(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if self.r_check(data[0], *(self.orders['writeLn'])):
            ast_writeLn = AST_WriteLn('writeLn', [])
            data[1].append(ast_writeLn)
            return (self.p_fu_function_call(((data[0][len(self.orders['writeLn'][0]):]),ast_writeLn))[0],data[1])
            
        return data
    
    # p_expression :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_expression(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if self.r_check(data[0], *(self.orders['exp'])) or self.r_check(data[0], *(self.orders['exp_2'])) or self.r_check(data[0], *(self.orders['exp_3'])) or self.r_check(data[0], *(self.orders['exp_4'])) or self.r_check(data[0], *(self.orders['open'])):
            ast_expression = AST_Expression('expression',[])
            data[1].append(ast_expression)
            return (self.p_fu_expression((data[0],ast_expression), ast_expression)[0],data[1])
        return data
    
    
    ## FOLLOW-UP PARSERS ##
    
    # p_fu_function :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_function(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_until_no_change(data, [self.p_function_param,self.p_function_first_param])
        if self.r_check(new_data[0], *(self.orders['func_close'])):
            new_data = self.p_function_def_closing(new_data)
        elif self.r_check(new_data[0], *(self.orders['func_ret'])):
            new_data = self.p_function_def_closing_ret(new_data)
        else:
            print(new_data)
            print("ERROR IN FUNCTION DEFINITION")
            return ([],data[1])
        return self.p_begin(new_data) #function body
    
    # p_fu_function_call :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_function_call(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_until_no_change(data, [self.p_function_call_param,self.p_function_call_first_param])
        if self.r_check(new_data[0], *(self.orders['close'])):
            return self.p_closing(new_data)
        else:
            print(new_data)
            print("ERROR IN PARENTHESES CLOSING")
            return ([],data[1])
    
    # p_fu_begin :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_begin(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return self.parse_until_no_change(data, [self.p_if,self.p_var,self.p_writeLn,self.p_expression])
    
    # p_fu_if :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_if(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return self.p_expression(data)

    # p_fu_expression :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_expression(self, data: Tuple[List[Token],AST_Node], head_node: AST_Expression) -> Tuple[List[Token],AST_Node]: 
        def _simple_insert_first_right(node: ExprNode, insertion_node: Union[ExprLeaf,ExprNode]) -> ExprNode:
            if node.right:
                _simple_insert_first_right(node.right,insertion_node) # since we are modifing the whole tree it makes sense to return the top node instead of only the directly modified node
            else:
                node.right = insertion_node
            return node
        
        def _insert(leaf: Union[ExprLeaf,ExprNode],node: ExprNode,current_node_in_tree:Union[ExprNode,AST_Expression]) -> AST_Expression:
            if not current_node_in_tree.right: # expression - []
                node.left = leaf
                current_node_in_tree.right = node
            elif current_node_in_tree.right and node > current_node_in_tree.right:
                return _insert(leaf,node,current_node_in_tree.right)
            else:
                node.left = current_node_in_tree.right
                current_node_in_tree.right = node
                _simple_insert_first_right(node.left,leaf)
            return head_node # still returning the head node since the whole tree is modified
        
        if   self.r_check(data[0], *(self.orders['open'])):   # ( )
            (data_0,data_1) = self.p_fu_expression((data[0][1:],data[1]), AST_Expression('expression',[]))
            print(data_1)
            data_1.right.precedence = 8
            if self.r_check(data_0, *(self.orders['op'])):
                head_node = _insert(data_1.right,ExprNode(data[0][0].data,self.get_precedence(data[0][0])),head_node)
                return self.p_fu_expression((data[0][1:],head_node),head_node)
            else:
                # weird leaf)) stuff (need to get rid of the extra expression node created)
                # might need more checks not sure
                # returning data_0 with head_node for now
                
                return (data_0,_simple_insert_first_right(head_node,data_1.right)) # removing the extra expression node

        elif self.r_check(data[0], *(self.orders['exp'])):    # variable
            head_node = _insert(ExprLeaf('var',data[0][0].data),ExprNode(data[0][1].data,self.get_precedence(data[0][1])),head_node)
            print(1)
            return self.p_fu_expression((data[0][len(self.orders['exp'][0]):],head_node),head_node)
        
        elif self.r_check(data[0], *(self.orders['exp_2'])):  # digit
            head_node = _insert(ExprLeaf('digit',data[0][0].data),ExprNode(data[0][1].data,self.get_precedence(data[0][1])),head_node)
            print(2)
            return self.p_fu_expression((data[0][len(self.orders['exp_2'][0]):],head_node),head_node)
        
        elif self.r_check(data[0], *(self.orders['exp_3'])):  # string
            head_node = _insert(ExprLeaf('string',data[0][0].data),ExprNode(data[0][1].data,self.get_precedence(data[0][1])),head_node)
            print(3)
            return self.p_fu_expression((data[0][len(self.orders['exp_3'][0]):],head_node),head_node)
        
        elif self.r_check(data[0], *(self.orders['exp_c'])) or self.r_check(data[0], *(self.orders['exp_s'])):  # var )
            head_node = _simple_insert_first_right(head_node,ExprLeaf('var',data[0][0].data))
            print(4)
            return (data[0][len(self.orders['exp_c'][0]):],head_node)

        elif self.r_check(data[0], *(self.orders['exp_2c'])) or self.r_check(data[0], *(self.orders['exp_2s'])): # digit ) or ;
            head_node = _simple_insert_first_right(head_node,ExprLeaf('digit',data[0][0].data))
            print(5)
            return (data[0][len(self.orders['exp_2c'][0]):],head_node)
        
        elif self.r_check(data[0], *(self.orders['exp_3c'])) or self.r_check(data[0], *(self.orders['exp_3s'])): # string )
            head_node = _simple_insert_first_right(head_node,ExprLeaf('string',data[0][0].data))
            print(6)
            return (data[0][len(self.orders['exp_3c'][0]):],head_node)
        
        elif self.r_check(data[0], *(self.orders['exp_4'])):  # functioncall
            (data_0 ,leaf_node_parent) = self.p_function((data[0][1:],AST_Temp))
            if self.r_check(data_0, *(self.orders['close'])) or self.r_check(data[0], *(self.orders['semi'])):    # (functioncall) ) or ;
                head_node = _simple_insert_first_right(head_node,leaf_node_parent.connections[0])
                return (data[0][len(self.orders['close'][0]):],head_node)
            else:
                expr_node = ExprNode(data_0[1].data,self.get_precedence(data_0[1]))
                head_node = _insert(leaf_node_parent.connections[0],expr_node,head_node)
                del leaf_node_parent
                return (data_0[1:],head_node)
        
        else:
            print("ERROR PARSER FAILED PARSING THIS EXPRESSION")
            print(data)
            print("")
            return data

          
    ## CLOSING PARSERS ##
    
    # p_function_first_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_first_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['first_param'])):
            ast_param = AST_FunctionParameter('param',[], data[0][0].data, data[0][2].data)
            data[1].append(ast_param)
            return ((data[0][len(self.orders['first_param'][0]):]),data[1])
        return data
    
    # p_function_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['params'])):
            ast_param = AST_FunctionParameter('param',[], data[0][1].data, data[0][3].data)
            data[1].append(ast_param)
            return ((data[0][len(self.orders['params'][0]):]),data[1])
        return data
    
    # p_function_call_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_call_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['list'])) or self.r_check(data[0], *(self.orders['str_list'])):
            ast_param = AST_Parameter('list',[], data[0][1].data, data[0][1].name)
            data[1].append(ast_param)
            return ((data[0][len(self.orders['list'][0]):]),data[1])
        return data
    
    # p_function_first_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_call_first_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['f_list']))or self.r_check(data[0], *(self.orders['str_f_list'])):
            ast_param = AST_Parameter('list',[], data[0][0].data, data[0][0].name)
            data[1].append(ast_param)
            return ((data[0][len(self.orders['f_list'][0]):]),data[1])
        return data
    
    # p_function_def_closing :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_def_closing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['func_close'])):
            return ((data[0][len(self.orders['func_close'][0]):]),data[1])
        return data
    
    # p_closing :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_closing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['close'])):
            return ((data[0][len(self.orders['close'][0]):]),data[1])
        return data
    
    # p_semicolomn :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_semicolomn(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['semi'])):
            return ((data[0][len(self.orders['semi'][0]):]),data[1])
        return data
    
    # p_end :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_end(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if self.r_check(data[0], *(self.orders['end'])):
            return ((data[0][len(self.orders['end'][0]):]),data[1])
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
        if not new_data[0] or len(data[0]) == len(new_data[0]):
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
    
    def parse_discard_until(self, data: Tuple[List[Token],AST_Node], token: Token) -> Tuple[List[Token],AST_Node]:
        # parser that discards all tokens untill it finds it Token. It will not discard the Token it tries to find
        if not len(data[0]) or data[0][0] == token:
            return data
        else:
            return self.parse_discard_until((data[0][1:],data[1]),token)
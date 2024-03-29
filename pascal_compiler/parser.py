from utils import *


# CLASS : Parser
# Brief : This class implements the parser functionality of pascal language
# Functions:
# The functions are divided by start parsers, follow-up parsers and closing parsers
# Start parsers are parsers that can be called from other parsers. These parsers are calling follow-up parsers.
# Follow-up parsers are parsers called from another parsering the same block. These follow-up parsers themselves can call 
# starting parsers, related follow-up parsers and closing parsers.
# Closing parser are parsers that don't call any other parsers and just return something after they have consumed a token
# All parsers return there input on failure to parse.
#
#
# self.orders : is a Dict that contains the order of tokens that needs to be parsed with their corresponding check functions (to be used in r_check function)
# self.precedence_order : precedence_order is a list that contains tuples of operators with their precedence. The higher the precedence the earlier it needs to be executed, 
# and thus the lower it will put placed in the expression tree
class Parser():
    def __init__(self):
        self.orders =           {'program' :    (   [Token('keyword','program')   ,Token('identifier')      ,Token('keyword',';')], 
                                                    [check_token_equal_all        ,check_token_equal_name   ,check_token_equal_all]),
                                 'var_dec' :    (   [Token('keyword','var')       ,Token('identifier')      ,Token('operator',':')      , Token('type')             ],
                                                    [check_token_equal_all        ,check_token_equal_name   ,check_token_equal_all      , check_token_equal_name    ]),                                     
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
                                 'var':         (   [Token('identifier')],
                                                    [check_token_equal_name]),
                                 'if' :         (   [Token('keyword','if')],
                                                    [check_token_equal_all]),
                                 'func_call':   (   [Token('identifier')          ,Token('parentheses_open')],
                                                    [check_token_equal_name       ,check_token_equal_name]),
                                 'writeLn':     (   [Token('keyword','WriteLn')   ,Token('parentheses_open')],
                                                    [check_token_equal_all        ,check_token_equal_name]),
                                 'readLn':      (   [Token('keyword','ReadLn')    ,Token('parentheses_open') ,Token('parentheses_closed')],
                                                    [check_token_equal_all        ,check_token_equal_name    ,check_token_equal_name]),
                                 'close':       (   [Token('parentheses_closed')],
                                                    [check_token_equal_name]),
                                 'close_op':    (   [Token('parentheses_closed'), Token('operator')],
                                                    [check_token_equal_name, check_token_equal_name]),
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
                                                    [check_token_equal_name]),
                                 'then':        (   [Token('keyword','then')],
                                                    [check_token_equal_all]),
                                 'str':         (   [Token('string')],
                                                    [check_token_equal_name]),
                                 'digit':       (   [Token('digit')],
                                                    [check_token_equal_name]),
                                 'id':          (   [Token('identifier')],
                                                    [check_token_equal_name]),
                                 'else':        (   [Token('keyword','else')],
                                                    [check_token_equal_all]),
                                 'eof':         (   [Token('eof','.')],
                                                    [check_token_equal_all]),
                                 'until':       (   [Token('keyword','until')],
                                                    [check_token_equal_all])
                                 
                                }
        self.precedence_order = [(Token('operator','<='),2),
                                 (Token('operator','>='),2),
                                 (Token('operator','='),2), 
                                 (Token('operator',':='),0), 
                                 (Token('operator','::='),0), 
                                 (Token('operator',':'),2), 
                                 (Token('operator','<'),2), 
                                 (Token('operator','>'),2), 
                                 (Token('operator','+'),3), 
                                 (Token('operator','-'),3), 
                                 (Token('operator','*'),4), 
                                 (Token('operator','/'),4),
                                 (Token('operator','or'),1),
                                 (Token('operator','and'),1),
                                 ]
    
    def __str__(self) -> str:
        return 'Parses the output from the lexer'
    __repr__ = __str__
    
    # get_precedence :: Token -> int
    def get_precedence(self, token: Token) -> int:
        def _get_precedence(po: List[Tuple[Token,int]]) -> int:  # in a functional language (haskell) this would have been a 'where'
            if len(po):
                if check_token_equal_all(token,po[0][0]):
                    return po[0][1]
                return _get_precedence(po[1:])
            return 9
        return _get_precedence(self.precedence_order)
    
    ## WRAPPERS ##
    
    # run :: [Token] -> AST_Node
    def run(self, tokens):
        return self.p_program(tokens)[1]
    
    ## INIT PARSER ##
    
    # The initial parser that needs to be called for every file/list of tokens that needs to be parsed.
    # p_program :: [Token] -> AST_Node
    def p_program(self, tokens: List[Token]) -> Tuple[List[Token],AST_Node]:
        if r_check(tokens, *(self.orders['program'])):   
            return self.p_eof(self.parse_until_no_change(((tokens[len(self.orders['program'][0]):]),AST_Program('program',[],tokens[1].name)), 
                                              [self.p_function,self.p_if,self.p_var,self.p_writeLn,self.p_readLn,self.p_function_call,self.p_repeat,self.p_expression,self.p_semicolon,self.p_begin]))
        else:
            print("No program identifier")
        return None

    
    ## START PARSERS ##
    
    # start parser for the function definitions
    # p_function :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_function(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['func'])):
            ast_function = AST_Function('function',[],data[0][1].data)
            data[1].append(ast_function)
            return (self.p_fu_function(((data[0][len(self.orders['func'][0]):]),ast_function))[0],data[1])
        else:
            return data
    
    # start parser for repeat statements
    # p_repeat :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_repeat(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['repeat'])):
            ast_repeat = AST_Repeat('repeat',[])
            data[1].append(ast_repeat)
            new_data = (self.p_fu_repeat_block(((data[0][len(self.orders['repeat'][0]):]),ast_repeat))[0],data[1])
            if r_check(new_data[0], *(self.orders['until'])):
                new_data = self.p_expression((new_data[0][1:],ast_repeat))
                return (new_data[0],data[1])
            print("No Until statement found for repeat")
            return new_data
        else:
            return data
    
    # start parser for begin blocks
    # p_begin :: ([Token], AST_Node) -> ([Token], AST_Node) 
    def p_begin(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['begin'])):
            ast_begin = AST_Begin('begin',[])
            data[1].append(ast_begin)
            return self.parse_in_order((self.p_fu_begin(((data[0][len(self.orders['begin'][0]):]),ast_begin))[0],data[1]), [self.p_end, self.p_semicolon])
        else:
            return data
    
    # start parser for variable declarations
    # p_var :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_var(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['var_dec'])):
            ast_var = AST_Var('var',[],data[0][1].data,data[0][3].data)
            data[1].append(ast_var)
            return (data[0][len(self.orders['var_dec'][0]):],data[1])
        else:
            return data
    
    # start parser for if statements
    # p_if :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_if(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if r_check(data[0], *(self.orders['if'])):
            ast_if = AST_If('if',[])
            data[1].append(ast_if)
            return (self.p_fu_if(((data[0][len(self.orders['if'][0]):]),ast_if))[0],data[1])
        else:
            return data
    
    # start parsers for function calls
    # p_function_call :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_function_call(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:  
        if r_check(data[0], *(self.orders['func_call'])):
            new_data = self.parse_discard_until_recursive(data,Token('parentheses_closed'),Token('parentheses_open'),1)
            if r_check(new_data[0],[Token('operator')],[check_token_equal_name]):
                return self.p_expression(data)
            function_call = AST_FunctionCall('func_call', [], data[0][0].data)
            data[1].append(function_call)
            if r_check(data[2:], *(self.orders['close'])):
                return (data[0][2:],data[1])
            return (self.p_fu_function_call(((data[0][len(self.orders['func_call'][0]):]),function_call))[0],data[1])   
        return data
    
    # start parsers for writeln (output) calls
    # p_writeLn :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_writeLn(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if r_check(data[0], *(self.orders['writeLn'])):
            ast_writeLn = AST_WriteLn('writeLn', [])
            data[1].append(ast_writeLn)
            return (self.p_fu_function_call(((data[0][len(self.orders['writeLn'][0]):]),ast_writeLn))[0],data[1])    
        return data
    
    # start parsers for readLn (input) calls
    # p_readLn :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_readLn(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if r_check(data[0], *(self.orders['readLn'])):
            ast_readLn = AST_ReadLn('readLn', [])
            data[1].append(ast_readLn)
            return (data[0][len(self.orders['readLn'][0]):],data[1])
        return data
    
    # start parsers for expressions
    # p_expression :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_expression(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if r_check(data[0], *(self.orders['exp'])) or r_check(data[0], *(self.orders['exp_2'])) or r_check(data[0], *(self.orders['exp_3'])) or (r_check(data[0], *(self.orders['func_call'])) and check_token_equal_name(self.parse_discard_until(data,Token('parentheses_closed'))[0][1],Token('operator'))) or r_check(data[0], *(self.orders['open'])):
            ast_expression = AST_Expression('expression',[])
            data[1].append(ast_expression)
            return (self.p_fu_expression((data[0],ast_expression), ast_expression, False)[0],data[1])
        return data
    
    
    ## FOLLOW-UP PARSERS ##
    
    # the follow-up parser for function declarations [p_function]
    # p_fu_function :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_function(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_until_no_change(data, [self.p_function_param,self.p_function_first_param])
        if r_check(new_data[0], *(self.orders['func_close'])):
            new_data = self.p_function_def_closing(new_data)
        elif r_check(new_data[0], *(self.orders['func_ret'])):
            new_data = self.p_function_def_closing_ret(new_data)
        else:
            print(new_data)
            print("ERROR IN FUNCTION DEFINITION")
            return ([],data[1])
        return self.p_begin(new_data) #function body
    
    # the follow-up parser for function calls [p_function_call]
    # p_fu_function_call :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_function_call(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_until_no_change(data, [self.p_function_call_param])
        if r_check(new_data[0], *(self.orders['close'])):
            return self.p_closing(new_data)
        else:
            # we have used the ) in the expression function
            print("We are missing the closing bracket")
            print(new_data)
            return new_data 
    
    # the follow-up parser for begin blocks [p_begin]
    # p_fu_begin :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_begin(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return self.parse_until_no_change(data, [self.p_repeat,self.p_if,self.p_var,self.p_writeLn,self.p_readLn,self.p_function_call,self.p_expression,self.p_semicolon])
    
    # the follow-up parser for if statements [p_if]
    # p_fu_if :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_if(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return self.p_fu_if_block(self.p_expression(data))
    
    # the follow-up parser for if statements [p_fu_if]
    # p_fu_if_block :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_if_block(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0],*(self.orders['then'])):
            if_true = AST_IfTrue('if_true',[])
            data[1].append(if_true)
            return self.p_semicolon(self.p_fu_if_else((self.parse_until_no_change((data[0][1:],if_true), [self.p_if,self.p_var,self.p_writeLn,self.p_readLn,self.p_function_call,self.p_expression])[0],data[1])))
        return data
    
    # the follow-up parser for if statements [p_fu_if_block]
    # p_fu_if_else :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_if_else(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]: 
        if r_check(data[0], *(self.orders['else'])):
            if_false = AST_IfFalse('if_false',[])
            data[1].append(if_false)
            return (self.p_semicolon(self.parse_until_no_change((data[0][1:],if_false), [self.p_if,self.p_var,self.p_writeLn,self.p_readLn,self.p_function_call,self.p_expression]))[0],data[1])
        return data

    # the follow-up parser for repeat statements [p_repeat]
    # p_fu_repeat_block :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_repeat_block(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        return self.p_semicolon(self.parse_until_no_change((data[0],data[1]), [self.p_repeat,self.p_if,self.p_var,self.p_writeLn,self.p_readLn,self.p_function_call,self.p_expression]))

    # the follow-up parser for expressions [p_fu_expression]
    
    # this parser knows it is inside an expression block
    # It takes two tokens at a time, a leaf token followed by an operator token
    # it inserts these tokens into the expression tree based on precedence
    # Has some edge cases for functioncall and parentheses but will treat them as leaf node followed by an operator node. (it only consumes more then 2 tokens at a single time)
    # p_fu_expression :: ([Token], AST_Node) -> ([Token], AST_Node)
    def p_fu_expression(self, data: Tuple[List[Token],AST_Node], head_node: AST_Expression, open: bool) -> Tuple[List[Token],AST_Node]: 
        
        # Simple inserts the node in the first right spot that is available in the tree (only going right)
        # _simple_insert_first_right :: ExprNode -> ExprLeaf | ExprNode -> ExprNode
        def _simple_insert_first_right(node: ExprNode, insertion_node: Union[ExprLeaf,ExprNode]) -> ExprNode:
            if node.right:
                _simple_insert_first_right(node.right,insertion_node) # since we are modifying the whole tree it makes sense to return the top node instead of only the directly modified node
            else:
                node.right = insertion_node
            return node
        
        # Inserts a node in the tree. A few cases are possible
        # case 1: We have reached the end of the expression tree - insert the new node at the end of the tree.
        # case 2: We have found a node equal or larger than our own nodes precedence - insert the new node at the current position and add the rest of the tree as our left node
        # case 3: We have found a node smaller than our own nodes precedence - move to the next node in the tree
        # when done we return the head node ( AST_Expression ) 
        # _insert :: ExprLeaf | ExprNode -> ASt_Expression | ExprNode -> AST_Expression
        def _insert(leaf: Union[ExprLeaf,ExprNode],node: ExprNode,current_node_in_tree:Union[ExprNode,AST_Expression]) -> AST_Expression:
            if not current_node_in_tree.right: ## the current node has no node on their right side. so we have reached the end of the expr tree
                node.left = leaf # make the lead ours
                current_node_in_tree.right = node # hang us at the end of the tree
            elif current_node_in_tree.right and node > current_node_in_tree.right: 
                return _insert(leaf,node,current_node_in_tree.right)
            else:
                node.left = current_node_in_tree.right
                current_node_in_tree.right = node
                _simple_insert_first_right(node.left,leaf)
            return head_node # still returning the head node since the whole tree is modified
        
        # Here we check for parentheses
        if   r_check(data[0], *(self.orders['open'])):   # ( )
            (data_0,data_1) = self.p_fu_expression((data[0][1:],data[1]), AST_Expression('expression',[]), True) # call yourself with a new expression node
            data_1.right.precedence = 8 # set the precedence really high so it will stay at the end of the expression tree
            if r_check(data_0, *(self.orders['op'])):  # insert into the tree with an operator
                head_node = _insert(data_1.right,ExprNode(data_0[0].data,self.get_precedence(data_0[0])),head_node)
                return self.p_fu_expression((data_0[1:],head_node),head_node, open)
            else: # this is a leaf
                if r_check(data_0, *(self.orders['close'])):
                    return (data_0[1:],_simple_insert_first_right(head_node,data_1.right)) # removing the extra ) *this is only possible in nested situations
                return (data_0,_simple_insert_first_right(head_node,data_1.right)) # removing the extra expression node

        elif r_check(data[0], *(self.orders['exp'])):    # variable
            head_node = _insert(ExprLeaf('var',data[0][0].data),ExprNode(data[0][1].data,self.get_precedence(data[0][1])),head_node)
            return self.p_fu_expression((data[0][len(self.orders['exp'][0]):],head_node),head_node,open)
        
        elif r_check(data[0], *(self.orders['exp_2'])):  # digit
            head_node = _insert(ExprLeaf('digit',data[0][0].data),ExprNode(data[0][1].data,self.get_precedence(data[0][1])),head_node)
            return self.p_fu_expression((data[0][len(self.orders['exp_2'][0]):],head_node),head_node,open)
        
        elif r_check(data[0], *(self.orders['exp_3'])):  # string
            head_node = _insert(ExprLeaf('string',data[0][0].data),ExprNode(data[0][1].data,self.get_precedence(data[0][1])),head_node)
            return self.p_fu_expression((data[0][len(self.orders['exp_3'][0]):],head_node),head_node,open)
        
        elif (open and r_check(data[0], *(self.orders['exp_c']))) or r_check(data[0], *(self.orders['exp_s'])):  # var )
            head_node = _simple_insert_first_right(head_node,ExprLeaf('var',data[0][0].data))
            return (data[0][len(self.orders['exp_c'][0]):],head_node)

        elif (open and r_check(data[0], *(self.orders['exp_2c']))): #or r_check(data[0], *(self.orders['exp_2s'])): # digit ) or ;
            head_node = _simple_insert_first_right(head_node,ExprLeaf('digit',data[0][0].data))
            return (data[0][len(self.orders['exp_2c'][0]):],head_node)
        
        elif (open and r_check(data[0], *(self.orders['exp_3c']))) or r_check(data[0], *(self.orders['exp_3s'])): # string )
            head_node = _simple_insert_first_right(head_node,ExprLeaf('string',data[0][0].data))
            return (data[0][len(self.orders['exp_3c'][0]):],head_node)
        
        elif r_check(data[0], *(self.orders['func_call'])) or r_check(data[0], *(self.orders['readLn'])):  # functioncall
            if r_check(data[0], *(self.orders['func_call'])):
                (data_0 ,leaf_node_parent) = self.p_function_call((data[0],AST_Temp()))
            else:
                (data_0 ,leaf_node_parent) = self.p_readLn((data[0],AST_Temp()))
            if r_check(data_0, *(self.orders['close'])):
                return (data_0[1:], head_node)
            if not r_check(data_0, *(self.orders['op'])):    # (functioncall) ) or ;
                head_node = _simple_insert_first_right(head_node,leaf_node_parent.connections[0])
                if r_check(data_0, *(self.orders['close'])) or r_check(data[0], *(self.orders['semi'])):
                    return (data_0[len(self.orders['close'][0]):],head_node)
                return (data_0,head_node)
            else:
                expr_node = ExprNode(data_0[0].data,self.get_precedence(data_0[0]))
                head_node = _insert(leaf_node_parent.connections[0],expr_node,head_node)      
                return self.p_fu_expression((data_0[1:],head_node),head_node,open)
        
        
        # no closing ')' or ';'
        elif r_check(data[0], *(self.orders['digit'])): # digit
            head_node = _simple_insert_first_right(head_node,ExprLeaf('digit',data[0][0].data))
            return (data[0][len(self.orders['digit'][0]):],head_node)
        
        elif r_check(data[0], *(self.orders['str'])): # string 
            head_node = _simple_insert_first_right(head_node,ExprLeaf('string',data[0][0].data))
            return (data[0][len(self.orders['str'][0]):],head_node)
        
        elif r_check(data[0], *(self.orders['var'])):  # var
            head_node = _simple_insert_first_right(head_node,ExprLeaf('var',data[0][0].data))
            return (data[0][len(self.orders['var'][0]):],head_node)
        
        else:
            print("ERROR PARSER FAILED PARSING THIS EXPRESSION")
            print(data)
            print("")
            return data

          
    ## CLOSING PARSERS ##
    
    # closing parser for function declaration [p_fu_function]
    # p_function_first_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_first_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['first_param'])):
            ast_param = AST_FunctionParameter('param',[], data[0][0].data, data[0][2].data)
            data[1].append(ast_param)
            return ((data[0][len(self.orders['first_param'][0]):]),data[1])
        return data
    
    # closing parser for function declaration [p_fu_function]
    # p_function_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['params'])):
            ast_param = AST_FunctionParameter('param',[], data[0][1].data, data[0][3].data)
            data[1].append(ast_param)
            return ((data[0][len(self.orders['params'][0]):]),data[1])
        return data
    
    # closing parser for function declaration [p_fu_function]
    # p_function_call_param :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_call_param(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        def inner_p_function_call_param_decorator(f) -> Tuple[List[Token],AST_Node]:
            def inner(data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
                if r_check(data[0],[Token('keyword',',')],[check_token_equal_all]):
                    return f((data[0][1:],data[1]))
                return f(data)
            return inner
        @inner_p_function_call_param_decorator
        def inner_p_function_call_param(data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
            if r_check(data[0], *(self.orders['close'])):
                return data
            
            if len(data[0]) >= 2 and ((check_token_equal_name(data[0][0], Token('parentheses_open')) or (check_token_equal_name(data[0][1], Token('operator'))))):
                new_data = self.p_expression((data[0],AST_Parameter('pexpr',[],'expression','expression')))
                data[1].append(new_data[1])
                return (new_data[0],data[1])
            
            if (r_check(data[0], *(self.orders['f_list']))):
                ast_param = AST_Parameter('pvar',[], data[0][0].data, data[0][0].name)
                data[1].append(ast_param)
                return ((data[0][len(self.orders['f_list'][0]):]),data[1])  
             
            if (r_check(data[0], *(self.orders['str_f_list']))) or (r_check(data[0], *(self.orders['digit']))):
                ast_param = AST_Parameter('pconst',[], data[0][0].data, data[0][0].name)
                data[1].append(ast_param)
                return ((data[0][len(self.orders['f_list'][0]):]),data[1])  
            
            
            return data
        return inner_p_function_call_param(data)
    
    # closing parser for the function definition [p_fu_function]
    # p_function_def_closing :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_def_closing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['func_close'])):
            return ((data[0][len(self.orders['func_close'][0]):]),data[1])
        return data
    
    # closing parser for a closing parentheses
    # p_closing :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_closing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['close'])):
            return ((data[0][len(self.orders['close'][0]):]),data[1])
        return data
    
    # closing parser for a trailing semicolon
    # p_semicolon :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_semicolon(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['semi'])):
            return ((data[0][len(self.orders['semi'][0]):]),data[1])
        return data
    
    # closing parser for a begin block 
    # p_end :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_end(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['end'])):
            return ((data[0][len(self.orders['end'][0]):]),data[1])
        return data
    
    # closing parser for the entire program
    # p_eof :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_eof(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['eof'])):
            return ((data[0][len(self.orders['eof'][0]):]),data[1])
        return data
    
    # closing parser for the function definition [p_fu_function]
    # p_function_def_closing_ret :: ([Token],AST_Node) -> ([Token], AST_Node)
    def p_function_def_closing_ret(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        if r_check(data[0], *(self.orders['func_ret'])):
            ast_return = AST_FunctionReturnType('func_ret',[], data[0][2].data)
            data[1].append(ast_return)
            return ((data[0][len(self.orders['func_ret'][0]):]),data[1])
        return data
    
    
    ## PARSER HELPERS ##
    
    # this parser keeps calling the parsers from the parsers list provided as a parameter until one of them succeeds. 
    # Then tries again from the start of the parser list until there is no change in the input data
    # parse_until_no_change :: ([Token], AST_Node) -> [(([Token],AST_Node) -> ([Token],AST_Node]))] -> ([Token], AST_Node)
    def parse_until_no_change(self, data: Tuple[List[Token],AST_Node], parsers: List[Callable[[Tuple[List[Token],AST_Node]],Tuple[List[Token],AST_Node]]]) -> Tuple[List[Token],AST_Node]:
        new_data = self.parse_in_order_stop_at_success(data, parsers)
        if not new_data[0] or len(data[0]) == len(new_data[0]):
            return new_data
        return self.parse_until_no_change(new_data, parsers)
    
    # parses using the provided parsers only once in order provided by the parser list
    # parse_in_order :: ([Token], AST_Node) -> [(([Token],AST_Node) -> ([Token],AST_Node]))] -> ([Token], AST_Node)
    def parse_in_order(self, data: Tuple[List[Token],AST_Node], parsers: List[Callable[[Tuple[List[Token],AST_Node]],Tuple[List[Token],AST_Node]]]) -> Tuple[List[Token],AST_Node]:
        parsers.reverse()
        parserall = compose(parsers)
        return parserall(data)

    # parses using the provided parsers only a single time in order provided by the parser list, Directly stops upon success
    # parse_in_order :: ([Token], AST_Node) -> [(([Token],AST_Node) -> ([Token],AST_Node]))] -> ([Token], AST_Node)
    def parse_in_order_stop_at_success(self, data: Tuple[List[Token],AST_Node], parsers: List[Callable[[Tuple[List[Token],AST_Node]],Tuple[List[Token],AST_Node]]]) -> Tuple[List[Token],AST_Node]:
        if not len(parsers):
            return data
        new_data = parsers[0](data)
        if not new_data[0] or len(data[0]) != len(new_data[0]):
            return new_data
        return self.parse_in_order_stop_at_success(data,parsers[1:])
    
    # parsers matching tokens. For example (), everything between the parentheses will be discarded. Nested parentheses will also be discarded.
    # parse_discard_until_recursive :: ([Token], AST_Node) -> Token -> Token -> int -> ([Token], AST_Node) 
    def parse_discard_until_recursive(self, data: Tuple[List[Token],AST_Node], token_stop: Token, token_start: Token, i: int) -> Tuple[List[Token],AST_Node]:
        if not len(data[0]):
            return data
        if data[0][0] == token_stop:
            if i - 1:
                return self.parse_discard_until_recursive((data[0][1:],data[1]),token_stop,token_start,i-1) 
            return data
        if data[0][0] == token_start:
            return self.parse_discard_until_recursive((data[0][1:],data[1]),token_stop,token_start,i+1) 
        else:
            return self.parse_discard_until_recursive((data[0][1:],data[1]),token_stop,token_start,i) 
    
    
    ## DEBUG PARSERS ##

    # does nothing returns input
    # parse_nothing :: ([Token],AST_Node) -> ([Token], AST_Node)
    def parse_nothing(self, data: Tuple[List[Token],AST_Node]) -> Tuple[List[Token],AST_Node]:
        # parser that parses nothing so to debug existing parsers :)
        return data
    
    # parses until it finds the token then stops without consuming the token
    # parse_nothing :: ([Token],AST_Node) -> Token -> ([Token], AST_Node)
    def parse_discard_until(self, data: Tuple[List[Token],AST_Node], token: Token) -> Tuple[List[Token],AST_Node]:
        # parser that discards all tokens until it finds it Token. It will not discard the Token it tries to find
        if not len(data[0]) or data[0][0] == token:
            return data
        else:
            return self.parse_discard_until((data[0][1:],data[1]),token)
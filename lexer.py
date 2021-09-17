from utils import *

# CLASS : Lexer
# Brief : This class implements the lexer functionality of pascal language
# Functions:
#
# lex_something: implements a lexer function that exepts a lambda function to make its return type
# it expects the following parameters 
# data: a tuple containing input and a list of output.
# check: a list that contains the various possible checks
# return_function: a function that generates output from the input when the check succeeds
# this function return a unmodified version of data when all checks fails
# it retuns a modified version of data when the first check passses.
#
# lex_something_between: implements a lexer function that expets a lambda function to make its return type
# it exepects the following parameters
# data: a tuple containing input and a list of output (tokens)
# chec
#
#
#
# lex_*: these functions lexs each token using the underlying *_something functions. The type of this function is (String, [Token]) -> (String, [Token])
# lex_all: runs all lex_* functions untill the no input is left. If an invalid program is provided this function will crash.
# run: wrapper around the lex_all function
class Lexer():
    def __init__(self):
        self.types =            ['integer', 'real', 'char', 'boolean', 'string']
        self.keywords =         ['var', 'repeat', 'while', 'do', 'until', 'WriteLn', 'begin', 'end', 'function', ',', ';', 'program', 'if', 'then', 'else']
        self.operators =        ['<=','>=','=', ':=', '::=', ':', '<', '>', '+', '-', '*', '/']
        self.brackets =         ['[',']']
        self.curly_bracket =    ['{','}']
        self.parentheses =      ['(',')']
        self.strings =          ['\'','"']
        self.digits =           [str(i) for i in range(10)]
        # composition of all the lex funtions (used in lex_all)
        self.lexall = compose([ self.lex_eof,
                                self.lex_skip_space, 
                                self.combine_digits,
                                self.lex_digit,
                                self.lex_types, 
                                self.lex_keywords, 
                                self.lex_operator,
                                self.lex_brackets, 
                                self.lex_curly_bracket, 
                                self.lex_parentheses, 
                                self.lex_strings
                              ])
        
    # lex_something :: ([a],[b]) -> a -> (a -> b) -> ([a],[b])
    def lex_something(self, data, check, return_function):
        if len(check):
            if check[0] == data[0][:len(check[0])]:
                data[1].append(return_function(check[0]))
                return (data[0][len(check[0]):], data[1])
            else:
                return self.lex_something(data, check[1:], return_function)
        return data

    # combine_same :: ([a],[b]) -> (([a],[b]) -> (c,d)) (c -> d -> bool) -> (([a],[b]) -> c -> d -> ([a],[b])) -> ([a],[b])
    def combine_something(self, data, get_function, check_function, combine_function):
        items = get_function(data)
        if items and check_function(*items):
            return combine_function(data,*items)
        return data
    
    # lex_something_between :: ([a],[b]) -> [a] -> [a] -> (a -> b) -> ([a],[b])
    def lex_something_between(self, data, begin, end, return_function):
        length = len(data[0])
        if length and data[0][0] in begin:
            def _psb(i):
                if i > length:
                    print("ERROR: lacking closing for: "+str(data[0][0]))
                    return ([],[])
                elif data[0][i] in end:
                    data[1].append(return_function(data[0][0:i]))
                    return (data[0][i+1:], data[1])
                return _psb(i+1)
            return _psb(1)
        return data
    
    # lex_types :: (String, [Token]) -> (String, [Token])
    def lex_types(self,         data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.types           ,(lambda v: Token("type",     v)))
    # lex_keywords :: (String, [Token]) -> (String, [Token])
    def lex_keywords(self,      data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.keywords        ,(lambda v: Token("keyword",  v)))
    # lex_operator :: (String, [Token]) -> (String, [Token])
    def lex_operator(self,      data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.operators       ,(lambda v: Token("operator", v)))
    # lex_brackets :: (String, [Token]) -> (String, [Token])
    def lex_brackets(self,      data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.brackets        ,(lambda v: Token("bracket_open"        ,'') if v == '[' else Token("bracket_closed"        ,'')))
    # lex_curly_bracket :: (String, [Token]) -> (String, [Token])
    def lex_curly_bracket(self, data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.curly_bracket   ,(lambda v: Token("curly_bracket_open"  ,'') if v == '{' else Token("curly_bracket_closed"  ,'')))
    # lex_parentheses :: (String, [Token]) -> (String, [Token])
    def lex_parentheses(self,   data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.parentheses     ,(lambda v: Token("parentheses_open"    ,'') if v == '(' else Token("parentheses_closed"    ,'')))
    # lex_strings :: (String, [Token]) -> (String, [Token])
    def lex_strings(self,       data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return functools.reduce(lambda d, c: self.lex_something_between(d,[c],[c],(lambda v: Token("string", v))), self.strings, data)
    # lex_eof :: (String, [Token]) -> (String, [Token])
    def lex_eof(self,       data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,['.']                ,(lambda v: Token("eof",      v)))
    # lex_digit :: (String, [Token]) -> (String, [Token])
    def lex_digit(self,       data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.lex_something(data,self.digits          ,(lambda v: Token("digit",    v)))
    # lex_skip_space :: (String, [Token]) -> (String, [Token])
    def lex_skip_space(self,    data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return data if len(data[0]) and data[0][0] != ' ' else (data[0][1:],data[1])
    # lex_identifier :: (String, [Token]) -> (String, [Token])
    def lex_identifier(self,    data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        def _lex_identifier(data: Tuple[str, List[Token]], current_identifier: str,i: int)  -> Tuple[str,int]:
            if data[0][i] != ' ' and data[0][i] not in (self.keywords + self.operators + self.parentheses):
                return _lex_identifier(data, (current_identifier + data[0][i]), (i + 1))
            else:
                return (current_identifier, i)
        current_identifier, i = _lex_identifier(data, "", 0)
        data[1].append(Token("identifier", current_identifier))
        return (data[0][i:],data[1])
    
    # combine_digits :: (String, [Token]) -> (String, [Token])
    def combine_digits(self,    data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        return self.combine_something(data,
                                      lambda d: (d[1][-1],d[1][-2]) if len(d[1]) > 1 else None, 
                                      lambda a,b: a.name == 'digit' and  b.name == a.name, 
                                      lambda d,a,b: (d[0],d[1][:-2]+[Token(a.name,b.data+a.data)]))
        
    # lex_all :: (String, [Token]) -> (String, [Token])    
    def lex_all(self,  data: Tuple[str, List[Token]]) -> Tuple[str, List[Token]]:
        new_data = self.lexall(data)
        if new_data == ("",[]):
            return ([],[Token("Lexer Error", "See above for error(s).")])
        if new_data[0] == "":
            return data
        elif new_data == data:
            new_data = self.lex_identifier(new_data)
            if new_data == data:
                print(data) # throw error
                return (data[0],[Token("Lexer Error", "Input could not be lexed. See remaining input for error(s).")])
        return self.lex_all(new_data)
    
    # run :: String -> [Token]
    def run(self, string: str) -> List[Token]:
        return self.lex_all((string,[]))[1]
    
    def __str__(self):
        return 'Lexes the following symbols:' + str([self.types,self.keywords,self.operators,self.brackets,self.curly_bracket,self.parentheses,self.strings,self.digits,[" "]])
    __repr__ = __str__
import io, sys
from lexer import *
#from parser import WendParser
from syntree import *
from analyzer import *
from transasm import *

class WendParser:
    stack = []

    def shift(self):
        self.stack.append(next(self.tokens, None))

    def chomp(self, pattern):
        l = len(pattern)
        if len(self.stack)<l: return None
        for s,p in zip(self.stack[-l:], pattern):
            if s.type != p:
                    return None
        t = self.stack[-l:]
        del self.stack[-l:]
        return t

    def parse(self, tokens):
        self.tokens = tokens
        self.shift()

        while self.stack and self.stack[-1] is not None:
            if t := self.chomp(['PRINT', 'STRING', 'SEMICOLON']):
                self.stack.append(Token('statement', Print(String(t[1].value, {'lineno':t[1].lineno} ), t[1].type=='println', {'lineno':t[1].lineno})))
#            elif t := self.chomp(['BEGIN', 'statement_list', 'END']):
#                self.stack.append(Token('fun_body', t[1].value))
            elif t := self.chomp(['statement_list', 'statement']):
                self.stack.append(Token('statement_list', t[0].value + [t[1].value]))
            elif t := self.chomp(['statement']):
                self.stack.append(Token('statement_list', [t[0].value]))
            elif t := self.chomp(['FUN', 'ID', 'LPAREN', 'RPAREN', 'BEGIN', 'statement_list', 'END']):
                self.stack.append(Token('fun', Function(t[1].value, [], [], [], t[5].value, {'lineno':t[1].lineno, 'type':Type.VOID})))
            else:
                self.shift()
#        print(self.stack)
        if len(self.stack)==2 and self.stack[0].type=='fun' and self.stack[1] is None:
            return self.stack[0].value
        return None
        
if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
try:
    f = open(sys.argv[1], 'r')
    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)
#    print(ast.name)
    build_symtable(ast)
    print(transasm(ast))
except Exception as e:
    print(e)


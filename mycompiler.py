import io, sys
from lexer import *
#from parser import WendParser
from syntree import *
from analyzer import *
from transasm import *

def tree_signature(n):
    if isinstance(n, Function):
        return 'Function{%s,%s}' % (''.join([tree_signature(f) for f in n.fun]), ''.join([tree_signature(s) for s in n.body]))
    elif isinstance(n, Print):
        return 'Print{%s}' % tree_signature(n.expr)
    elif isinstance(n, Return):
        return 'Return{%s}' % tree_signature(n.expr)
    elif isinstance(n, Assign):
        return 'Assign{%s}' % tree_signature(n.expr)
    elif isinstance(n, FunCall):
        return 'FunCall{%s}' % ','.join([tree_signature(e) for e in n.args])
    elif isinstance(n, While):
        return 'While{%s,%s}' % (tree_signature(n.expr), ''.join([tree_signature(s) for s in n.body]))
    elif isinstance(n, IfThenElse):
        return 'IfThenElse{%s,%s,%s}' % (tree_signature(n.expr), ''.join([tree_signature(s) for s in n.ibody]), ''.join([tree_signature(s) for s in n.ebody]))
    elif isinstance(n, ArithOp):
        return 'ArithOp{%s,%s,%s}' % (n.op, tree_signature(n.left), tree_signature(n.right))
    elif isinstance(n, LogicOp):
        return 'LogicOp{%s,%s}' % (tree_signature(n.left), tree_signature(n.right))
    elif isinstance(n, Integer):
        return 'Integer{%d}' % n.value
    elif isinstance(n, Boolean):
        return 'Boolean'
    elif isinstance(n, Var):
        return 'Var'
    elif isinstance(n, String):
        return 'String'
    return ''


class WendParser:
    stack, lookahead = [], None

    def shift(self):
        self.stack.append(self.lookahead or next(self.tokens, None))
        self.lookahead = next(self.tokens, None)

    def chomp(self, match, avoid_behind=[], avoid_ahead=[]):
        self.chew = None
        match = match.split(' ')
        l = len(match)
        if (len(self.stack)<l or
                (len(self.stack)>=l+1 and self.stack[-(l+1)].type in avoid_behind) or
                (self.lookahead and self.lookahead.type in avoid_ahead)):
            return None
        for s,p in zip(self.stack[-l:], match):
            if s.type != p:
                    return None
        self.chew = self.stack[-l:]
        del self.stack[-l:]
        return self.chew

    def parse(self, tokens):
        self.tokens = tokens
        self.shift()

        while self.stack and self.stack[-1] is not None:
            if self.chomp('TYPE'):
                self.stack.append(Token('type', Type.INT if self.chew[0].value=='int' else Type.BOOL))
            elif self.chomp('BOOLVAL'):
                self.stack.append(Token('expr', Boolean(self.chew[0].value=='true', {'lineno':self.chew[0].lineno})))
            elif self.chomp('INTVAL'):
                self.stack.append(Token('expr', Integer(int(self.chew[0].value), {'lineno':self.chew[0].lineno})))
            elif self.chomp('STRING'):
                self.stack.append(Token('expr', String(self.chew[0].value, {'lineno':self.chew[0].lineno})))
            elif self.chomp('ID', [], ['LPAREN', 'COLON', 'ASSIGN']):
                self.stack.append(Token('expr', Var(self.chew[0].value, {'lineno':self.chew[0].lineno})))
            elif self.chomp('MINUS expr', ['expr'], []): # unary minus
                self.stack.append(Token('expr', ArithOp('-', Integer(0), self.chew[1].value, {'lineno':self.chew[1].lineno})))
            elif self.chomp('PLUS expr', ['expr'], []): # unary plus
                self.stack.append(self.chew[1])
            elif self.chomp('LPAREN expr RPAREN', ['ID'], []): # do not confuse with FunCall
                self.stack.append(self.chew[1])
            elif self.chomp('ID LPAREN expr RPAREN', [], ['SEMICOLON']): # do not confuse with FunCall statement
                self.stack.append(Token('expr', FunCall(self.chew[0].value, [self.chew[1].value], {'lineno':self.chew[0].lineno})))
            elif (self.chomp('expr TIMES expr')  or
                  self.chomp('expr DIVIDE expr') or
                  self.chomp('expr MOD expr')    or
                  self.chomp('expr PLUS expr',  [], ['TIMES', 'DIVIDE', 'MOD']) or
                  self.chomp('expr MINUS expr', [], ['TIMES', 'DIVIDE', 'MOD'])):
                self.stack.append(Token('expr', ArithOp(self.chew[1].value, self.chew[0].value, self.chew[2].value, {'lineno':self.chew[0].lineno})))
            elif self.chomp('NOT expr'):
                self.stack.append(Token('expr', LogicOp('==', Boolean(False), self.chew[1].value, {'lineno':self.chew[1].lineno})))
            elif (self.chomp('expr COMP expr') or
                  self.chomp('expr AND expr',  [], ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD']) or
                  self.chomp('expr OR expr', [], ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'AND'])):
                self.stack.append(Token('expr', LogicOp(self.chew[1].value, self.chew[0].value, self.chew[2].value, {'lineno':self.chew[0].lineno})))
            elif self.chomp('ID ASSIGN expr SEMICOLON'):
                self.stack.append(Token('statement', Assign(self.chew[0].value, self.chew[2].value, {'lineno':self.chew[0].lineno})))
            elif self.chomp('RETURN expr SEMICOLON'):
                self.stack.append(Token('statement', Return(self.chew[1].value, {'lineno':self.chew[0].lineno})))
            elif self.chomp('RETURN SEMICOLON'):
                self.stack.append(Token('statement', Return(None, {'lineno':self.chew[0].lineno})))
            elif self.chomp('PRINT expr SEMICOLON'):
                self.stack.append(Token('statement', Print(self.chew[1].value, self.chew[0].value=='println', {'lineno':self.chew[0].lineno})))
            elif self.chomp('statement_list statement'):
                self.stack.append(Token('statement_list', self.chew[0].value + [self.chew[1].value]))
            elif self.chomp('statement'):
                self.stack.append(Token('statement_list', [self.chew[0].value]))
            elif self.chomp('FUN ID LPAREN RPAREN BEGIN statement_list END'):
                self.stack.append(Token('fun', Function(self.chew[1].value, [], [], [], self.chew[5].value, {'lineno':self.chew[1].lineno, 'type':Type.VOID})))
            else:
                self.shift()
        print(self.stack)
        if len(self.stack)==2 and self.stack[0].type=='fun' and self.stack[1] is None:
            return self.stack[0].value
        return None

if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
try:
    f = open(sys.argv[1], 'r')
    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)
    print(tree_signature(ast))
#    build_symtable(ast)
#    print(transasm(ast))
except Exception as e:
    print(e)


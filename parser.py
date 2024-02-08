from sly import Parser
from lexer import WendLexer
from syntree import *

class WendParser(Parser):
    tokens = WendLexer.tokens
    debugfile = 'parser.out'

    @_('FUN ID LPAREN param_list RPAREN fun_type BEGIN var_list fun_list statement_list END')
    def fun(self, p):
        return Function(p[1], p.param_list or [], p.var_list or [],  p.fun_list or [], p.statement_list or [], {'type':p.fun_type})

    @_('ID COLON TYPE')
    def var(self, p):
        return (p[0], {'type':Type.INT if p[2]=='int' else Type.BOOL, 'lineno':p.lineno})

    @_('var')
    def param_list(self, p):
        return [ p.var ]

    @_('')
    def param_list(self, p):
        return [ ]

    @_('param_list COMMA var')
    def param_list(self, p):
        return p.param_list + [ p.var ]

    @_('COLON TYPE')
    def fun_type(self, p):
        return Type.INT if p[1]=='int' else Type.BOOL

    @_('')
    def fun_type(self, p):
        return Type.VOID

    @_('var_list VAR var SEMICOLON')
    def var_list(self, p):
        return p.var_list + [p.var]

    @_('')
    def var_list(self, p):
        return []

    @_('')
    def fun_list(self, p):
        return []

    @_('fun_list fun')
    def fun_list(self, p):
        return p.fun_list + [p.fun]

    @_('')
    def statement_list(self, p):
        return []

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('WHILE expr BEGIN statement_list END')
    def statement(self, p):
        return While(p.expr, p.statement_list or [], {'lineno':p.lineno})

    @_('IF expr BEGIN statement_list END else_statement')
    def statement(self, p):
        return IfThenElse(p.expr, p.statement_list or [], p.else_statement or [], {'lineno':p.lineno})

    @_('')
    def else_statement(self, p):
        return []

    @_('ELSE BEGIN statement_list END')
    def else_statement(self, p):
        return p.statement_list

    @_('PRINT expr SEMICOLON')
    def statement(self, p):
        return Print(p.expr, p[0]=='println', {'lineno':p.lineno})

    @_('RETURN SEMICOLON')
    def statement(self, p):
        return Return(None, {'lineno':p.lineno})

    @_('RETURN expr SEMICOLON')
    def statement(self, p):
        return Return(p.expr, {'lineno':p.lineno})

    @_('ID ASSIGN expr SEMICOLON')
    def statement(self, p):
        return Assign(p[0], p.expr, {'lineno':p.lineno})

    @_('ID LPAREN arg_list RPAREN SEMICOLON')
    def statement(self, p):
        return FunCall(p[0], p.arg_list or [], {'lineno':p.lineno})

    @_('arg_list COMMA expr')
    def arg_list(self, p):
        return p.arg_list + [ p.expr ]

    @_('')
    def arg_list(self, p):
        return []

    @_('expr')
    def arg_list(self, p):
        return [ p.expr ]

    @_('STRING')
    def expr(self, p):
        return String(p[0], {'lineno':p.lineno})

    @_('expr OR conjunction')
    def expr(self, p):
        return LogicOp(p[1], p.expr, p.conjunction, {'lineno':p.lineno})

    @_('conjunction')
    def expr(self, p):
        return p.conjunction

    @_('conjunction AND literal')
    def conjunction(self, p):
        return LogicOp(p[1], p.conjunction, p.literal, {'lineno':p.lineno})

    @_('literal')
    def conjunction(self, p):
        return p.literal

    @_('comparand')
    def literal(self, p):
        return p.comparand

    @_('NOT comparand')
    def literal(self, p):
        return LogicOp('==', Boolean(False), p.comparand, {'lineno':p.lineno})

    @_('addend COMP addend')
    def comparand(self, p):
        return LogicOp(p[1], p.addend0, p.addend1, {'lineno':p.lineno})

    @_('addend')
    def comparand(self, p):
        return p.addend

    @_('addend PLUS term',
       'addend MINUS term')
    def addend(self, p):
        return ArithOp(p[1], p.addend, p.term, {'lineno':p.lineno})

    @_('term')
    def addend(self, p):
        return p.term

    @_('term TIMES factor',
       'term DIVIDE factor',
       'term MOD factor')
    def term(self, p):
        return ArithOp(p[1], p.term, p.factor, {'lineno':p.lineno})

    @_('factor')
    def term(self, p):
        return p.factor

    @_('MINUS atom')
    def factor(self, p):
        return ArithOp('-', Integer(0), p.atom, {'lineno':p.lineno})

    @_('atom', 'PLUS atom')
    def factor(self, p):
        return p.atom

    @_('LPAREN expr RPAREN')
    def atom(self, p):
        return p.expr

    @_('ID')
    def atom(self, p):
        return Var(p[0], {'lineno':p.lineno})

    @_('ID LPAREN arg_list RPAREN')
    def atom(self, p):
        return FunCall(p[0], p.arg_list or [], {'lineno':p.lineno})

    @_('INTVAL')
    def atom(self, p):
        return Integer(int(p.INTVAL), {'lineno':p.lineno})

    @_('BOOLVAL')
    def atom(self, p):
        return Boolean(p.BOOLVAL=='true', {'lineno':p.lineno})

    def error(self, token):
        if not token:
            raise Exception('Syntax error: unexpected EOF')
        raise Exception(f'Syntax error at line {token.lineno}, token={token.type}')

from sly import Parser
from lexer import WendLexer
from syntree import *

class WendParser(Parser):
    tokens = WendLexer.tokens
    debugfile = 'parser.out'

    precedence = ( # arithmetic operators take precedence over logical operators
         ('left', OR),
         ('left', AND),
         ('right', NOT),
         ('nonassoc', COMP),
         ('left', PLUS, MINUS),
         ('left', TIMES, DIVIDE, MOD),
         ('right', UMINUS), # unary operators
         ('right', UPLUS)
    )

    @_('FUN ID LPAREN param_list RPAREN type_optional BEGIN var_list fun_list statement_list END')
    def fun(self, p):
        return Function(p[1], p.param_list or [], p.var_list or [],  p.fun_list or [], p.statement_list or [], {'type':p.type_optional})

    @_('param_list COMMA param')
    def param_list(self, p):
        return p.param_list + [ p.param ]

    @_('')
    def param_list(self, p):
        return [ ]

    @_('param')
    def param_list(self, p):
        return [ p.param ]

    @_('ID COLON TYPE')
    def param(self, p):
        return (p[0], {'type':Type.INT if p[2]=='int' else Type.BOOL, 'lineno':p.lineno})

    @_('var_list var')
    def var_list(self, p):
        return p.var_list + [p.var]

    @_('')
    def var_list(self, p):
        return []

    @_('VAR ID COLON TYPE SEMICOLON')
    def var(self, p):
        return (p[1], {'type':Type.INT if p[3]=='int' else Type.BOOL, 'lineno':p.lineno})

    @_('fun_list fun')
    def fun_list(self, p):
        return p.fun_list + [p.fun]

    @_('')
    def fun_list(self, p):
        return []

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('')
    def statement_list(self, p):
        return []

    @_('WHILE expr BEGIN statement_list END')
    def statement(self, p):
        return While(p.expr, p.statement_list or [], {'lineno':p.lineno})

    @_('IF expr BEGIN statement_list END [ ELSE BEGIN statement_list END ]')
    def statement(self, p):
        return IfThenElse(p.expr, p.statement_list0 or [], p.statement_list1 or [], {'lineno':p.lineno})

    @_('PRINT expr SEMICOLON')
    def statement(self, p):
        return Print(p.expr, p[0]=='println', {'lineno':p.lineno})

    @_('RETURN [ expr ] SEMICOLON')
    def statement(self, p):
        return Return(p.expr or None, {'lineno':p.lineno})

    @_('ID ASSIGN expr SEMICOLON')
    def statement(self, p):
        return Assign(p[0], p.expr, {'lineno':p.lineno})

    @_('ID LPAREN args RPAREN SEMICOLON')
    def statement(self, p):
        return FunCall(p[0], p.args or [], {'lineno':p.lineno})

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return ArithOp('-', Integer(0), p.expr, {'lineno':p.lineno})

    @_('PLUS expr %prec UPLUS',
       'LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr TIMES expr',
       'expr DIVIDE expr',
       'expr MOD expr')
    def expr(self, p):
        return ArithOp(p[1], p.expr0, p.expr1, {'lineno':p.lineno})

    @_('expr COMP expr',
       'expr AND expr',
       'expr OR expr')
    def expr(self, p):
        return LogicOp(p[1], p.expr0, p.expr1, {'lineno':p.lineno})

    @_('NOT expr')
    def expr(self, p):
        return LogicOp('==', Boolean(False), p.expr, {'lineno':p.lineno})

    @_('ID')
    def expr(self, p):
        return Var(p[0], {'lineno':p.lineno})

    @_('ID LPAREN args RPAREN')
    def expr(self, p):
        return FunCall(p[0], p.args or [], {'lineno':p.lineno})

    @_('args COMMA expr')
    def args(self, p):
        return p.args + [ p.expr ]

    @_('')
    def args(self, p):
        return []

    @_('expr')
    def args(self, p):
        return [ p.expr ]

    @_('STRING')
    def expr(self, p):
        return String(p[0], {'lineno':p.lineno})

    @_('INTVAL')
    def expr(self, p):
        return Integer(int(p.INTVAL), {'lineno':p.lineno})

    @_('BOOLVAL')
    def expr(self, p):
        return Boolean(p.BOOLVAL=='true', {'lineno':p.lineno})

    @_('COLON TYPE')
    def type_optional(self, p):
        return Type.INT if p[1]=='int' else Type.BOOL

    @_('')
    def type_optional(self, p):
        return Type.VOID

    def error(self, token):
        if not token:
            raise Exception('Syntax error: unexpected EOF')
        raise Exception(f'Syntax error at line {token.lineno}, token={token.type}')

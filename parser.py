from sly import Parser
from lexer import WendLexer
from syntree import *

class WendParser(Parser):
    tokens = WendLexer.tokens

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

    @_('fun_decl fun_body')
    def fun(self, p):
        return Function(*(p.fun_decl[:-1] + p.fun_body), p.fun_decl[-1])

    @_('FUN ID LPAREN [ param_list ] RPAREN [ COLON type ]')
    def fun_decl(self, p):
        deco, name, params = {'type':(p.type or Type.VOID), 'lineno':p.lineno}, p[1], (p.param_list or [])
        return [name, params, deco]

    @_('param { COMMA param }')
    def param_list(self, p):
        return [p.param0] + p.param1

    @_('ID COLON type')
    def param(self, p):
        return (p[0], {'type':p.type, 'lineno':p.lineno})

    @_('BEGIN [ var_list ] [ fun_list ] [ statement_list ] END')
    def fun_body(self, p):
        return [p.var_list or [], p.fun_list or [], p.statement_list or []]

    @_('var { var }')
    def var_list(self, p):
        return [p.var0] + p.var1

    @_('VAR ID COLON type SEMICOLON')
    def var(self, p):
        return (p[1], {'type':p.type, 'lineno':p.lineno})

    @_('fun { fun }')
    def fun_list(self, p):
        return [p.fun0] + p.fun1

    @_('statement { statement }')
    def statement_list(self, p):
        return [p.statement0] + p.statement1

    @_('WHILE expr BEGIN [ statement_list ] END')
    def statement(self, p):
        return While(p.expr, p.statement_list or [], {'lineno':p.lineno})

    @_('IF expr BEGIN [ statement_list ] END [ ELSE BEGIN statement_list_optional END ]')
    def statement(self, p):
        return IfThenElse(p.expr, p.statement_list or [], p.statement_list_optional or [], {'lineno':p.lineno})

    @_('statement_list')                  # sly does not support nested
    def statement_list_optional(self, p): # optional targets, therefore
        return p.statement_list           # this rule

    @_('')
    def statement_list_optional(self, p):
        return []

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

    @_('ID LPAREN [ args ] RPAREN SEMICOLON')
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

    @_('ID LPAREN [ args ] RPAREN')
    def expr(self, p):
        return FunCall(p[0], p.args or [], {'lineno':p.lineno})

    @_('expr { COMMA expr }')
    def args(self, p):
        return [p.expr0] + p.expr1

    @_('STRING')
    def expr(self, p):
        return String(p[0], {'lineno':p.lineno})

    @_('INTVAL')
    def expr(self, p):
        return Integer(int(p.INTVAL), {'lineno':p.lineno})

    @_('BOOLVAL')
    def expr(self, p):
        return Boolean(p.BOOLVAL=='true', {'lineno':p.lineno})

    @_('TYPE')
    def type(self, p):
        return Type.INT if p[0]=='int' else Type.BOOL

    def error(self, token):
        if not token:
            raise Exception('Syntax error: unexpected EOF')
        raise Exception(f'Syntax error at line {token.lineno}, token={token.type}')

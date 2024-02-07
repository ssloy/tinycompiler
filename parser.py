from sly import Parser
from lexer import WendLexer
from syntree import *

class WendParser(Parser):
    tokens = WendLexer.tokens
    debugfile = 'parser.out'

#    precedence = ( # arithmetic operators take precedence over logical operators
#        ('left', OR),
#        ('left', AND),
#         ('right', NOT),
#         ('nonassoc', COMP),
#        ('left', PLUS, MINUS),
#        ('left', TIMES, DIVIDE, MOD),
#         ('right', UMINUS), # unary operators
#         ('right', UPLUS)
#    )

    @_('FUN ID LPAREN param_list RPAREN fun_type BEGIN var_list fun_list statement_list END')
    def fun(self, p):
        return Function(p[1], p.param_list or [], p.var_list or [],  p.fun_list or [], p.statement_list or [], {'type':p.fun_type})

    @_('param_list COMMA var')
    def param_list(self, p):
        return p.param_list + [ p.var ]

    @_('')
    def param_list(self, p):
        return [ ]

    @_('var')
    def param_list(self, p):
        return [ p.var ]

    @_('var_list VAR var SEMICOLON')
    def var_list(self, p):
        return p.var_list + [p.var]

    @_('')
    def var_list(self, p):
        return []

    @_('ID COLON TYPE')
    def var(self, p):
        return (p[0], {'type':Type.INT if p[2]=='int' else Type.BOOL, 'lineno':p.lineno})

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

#   @_('MINUS expr %prec UMINUS')
#   def expr(self, p):
#       return ArithOp('-', Integer(0), p.expr, {'lineno':p.lineno})

#   @_('PLUS expr %prec UPLUS')
#   def expr(self, p):
#       return p.expr

#   @_('expr PLUS expr',
#      'expr MINUS expr',
#      'expr TIMES expr',
#      'expr DIVIDE expr',
#      'expr MOD expr')
#   def expr(self, p):
#       return ArithOp(p[1], p.expr0, p.expr1, {'lineno':p.lineno})

#   @_('expr COMP expr')
#   def expr(self, p):
#       return LogicOp(p[1], p.expr0, p.expr1, {'lineno':p.lineno})

#   @_('LPAREN expr RPAREN')
#   def expr(self, p):
#       return p.expr


#    @_('NOT expr')
#    def expr(self, p):
#        return LogicOp('==', Boolean(False), p.expr, {'lineno':p.lineno})

#   @_('ID')
#   def expr(self, p):
#       return Var(p[0], {'lineno':p.lineno})

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

    @_('expr_a')
    def expr(self, p):
        return p.expr_a

    @_('expr_d')
    def expr(self, p):
        return p.expr_d

    @_('expr_e COMP expr_e')
    def expr_d(self, p):
        return LogicOp(p[1], p.expr_e0, p.expr_e1, {'lineno':p.lineno})

    @_('expr_e')
    def expr_d(self, p):
        return p.expr_e



    @_('expr_e PLUS expr_t',
       'expr_e MINUS expr_t')
    def expr_e(self, p):
        return ArithOp(p[1], p.expr_e, p.expr_t, {'lineno':p.lineno})

    @_('expr_t')
    def expr_e(self, p):
        return p.expr_t

    @_('expr_t TIMES expr_p',
       'expr_t DIVIDE expr_p',
       'expr_t MOD expr_p')
    def expr_t(self, p):
        return ArithOp(p[1], p.expr_t, p.expr_p, {'lineno':p.lineno})

    @_('expr_p')
    def expr_t(self, p):
        return p.expr_p

    @_('MINUS expr_p')
    def expr_p(self, p):
        return ArithOp('-', Integer(0), p.expr_p, {'lineno':p.lineno})

    @_('PLUS expr_p')
    def expr_p(self, p):
        return p.expr_p

    @_('expr_final')
    def expr_p(self, p):
        return p.expr_final

    @_('LPAREN expr RPAREN')
    def expr_final(self, p):
        return p.expr

    @_('ID')
    def expr_final(self, p):
        return Var(p[0], {'lineno':p.lineno})

    @_('ID LPAREN arg_list RPAREN')
    def expr_final(self, p):
        return FunCall(p[0], p.arg_list or [], {'lineno':p.lineno})

    @_('INTVAL')
    def expr_final(self, p):
        return Integer(int(p.INTVAL), {'lineno':p.lineno})

    @_('BOOLVAL')
    def expr_final(self, p):
        return Boolean(p.BOOLVAL=='true', {'lineno':p.lineno})

    @_('expr_a OR expr_b')
    def expr_a(self, p):
        return LogicOp(p[1], p.expr_a, p.expr_b, {'lineno':p.lineno})

    @_('expr_b')
    def expr_a(self, p):
        return p.expr_b

    @_('expr_b AND expr_c')
    def expr_b(self, p):
        return LogicOp(p[1], p.expr_b, p.expr_c, {'lineno':p.lineno})

#   @_('expr_b AND expr_d')
#   def expr_b(self, p):
#       return LogicOp(p[1], p.expr_b, p.expr_d, {'lineno':p.lineno})

    @_('expr_c')
    def expr_b(self, p):
        return p.expr_c

    @_('NOT expr_final')
    def expr_c(self, p):
        return LogicOp('==', Boolean(False), p.expr_final, {'lineno':p.lineno})

    @_('COLON TYPE')
    def fun_type(self, p):
        return Type.INT if p[1]=='int' else Type.BOOL

    @_('')
    def fun_type(self, p):
        return Type.VOID

    def error(self, token):
        if not token:
            raise Exception('Syntax error: unexpected EOF')
        raise Exception(f'Syntax error at line {token.lineno}, token={token.type}')

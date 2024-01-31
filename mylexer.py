import io, sys

class Token(object):
    def __init__(self, t, v, l):
        self.type, self.value, self.lineno = t, v, l+1 # mwahaha, +1, sly, wtf?
        self.index = None
        self.end = None

    def __repr__(self):
        return f'Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno!r})'

def tokenize(text):
    kwd    = {'true':'BOOLVAL','false':'BOOLVAL','print':'PRINT','println':'PRINTLN','int':'INT','bool':'BOOL','var':'VAR','fun':'FUN','if':'IF','else':'ELSE','while':'WHILE','return':'RETURN'}
    double = {'==':'EQ', '<=':'LTEQ', '>=':'GTEQ', '!=':'NOTEQ', '&&':'AND', '||':'OR'}
    single = {'=':'ASSIGN','<':'LT', '>':'GT', '!':'NOT', '+':'PLUS', '-':'MINUS', '/':'DIVIDE', '*':'TIMES', '%':'MOD','(':'LPAREN',')':'RPAREN', '{':'BEGIN', '}':'END', ';':'SEMICOLON', ':':'COLON', ',':'COMMA'}

    lineno, idx, state, accum = 0, 0, 0, ''
    while idx<len(text):
        sym1 = text[idx+0] if idx<len(text)-0 else ' '
        sym2 = text[idx+1] if idx<len(text)-1 else ' '
        if sym1 == '\n':
            lineno += 1
        if state==0: # start of a token
            if sym1 == '/' and sym2 == '/':
                state = 1 # comment
            elif sym1.isalpha() or sym1=='_':
                state = 3 # word
                accum += sym1
            elif sym1.isdigit():
                state = 4 # number
                accum += sym1
            elif sym1 == '"':
                state = 2 # string
            elif sym1 + sym2 in double:
                yield Token(double[sym1+sym2], sym1+sym2, lineno)
                idx += 1
            elif sym1 in single:
                yield Token(single[sym1], sym1, lineno)
        elif state==1: # comment
            if sym2 == '\n':
                state = 0 # restart
        elif state==3: # word
            if sym1.isalpha() or sym1=='_' or  sym1.isdigit():
                accum += sym1
            else:
                if accum in kwd:
                    yield Token(kwd[accum], accum, lineno)
                else:
                    yield Token('ID', accum, lineno)
                accum = ''
                idx -= 1
                state = 0 # restart
        elif state==4: # number
            if sym1.isdigit():
                accum += sym1
            else:
                yield Token('INTVAL', accum, lineno)
                idx -= 1
                accum = ''
                state = 0 # restart
        elif state==2: # string
            if sym1 != '"':
                accum += sym1
            else:
                yield Token('STRING', f'"{accum}"', lineno)
                accum = ''
                state = 0 # restart
        idx += 1
    if state!=0:
        raise Exception('Lexical error: unexpected EOF')

import io, sys

class Token(object):
    def __init__(self, t, v, l):
        self.type, self.value, self.lineno = t, v, l+1 # mwahaha, +1, sly, wtf?
        self.index = None
        self.end = None

    def __repr__(self):
        return f'Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno!r})'

class State:
    START   = 0
    COMMENT = 1
    STRING  = 2
    WORD    = 3
    NUMBER  = 4

def tokenize(text):
    lineno, idx = 0, 0
    accum = ''
    state = State.START
    while idx<len(text):
        sym1 = text[idx+0] if idx<len(text)-0 else ' '
        sym2 = text[idx+1] if idx<len(text)-1 else ' '
#            print(sym1, sym2)
        if sym1 == '\n':
            lineno += 1
        if state==State.START:
            if sym1 == '/' and sym2 == '/':
                state = State.COMMENT
            elif sym1.isalpha() or sym1=='_':
                state = State.WORD
                accum += sym1
            elif sym1.isdigit():
                state = State.NUMBER
                accum += sym1
            elif sym1 == '"':
                state = State.STRING
            elif sym1 == '=':
                if sym2 == '=':
                    yield Token('EQ', '==', lineno)
                    idx += 1
                else:
                    yield Token('ASSIGN', '=', lineno)
            elif sym1 == '<':
                if sym2 == '=':
                    yield Token('LTEQ', '<=', lineno)
                    idx += 1
                else:
                    yield Token('LT', '<', lineno)
            elif sym1 == '>':
                if sym2 == '=':
                    yield Token('GTEQ', '>=', lineno)
                    idx += 1
                else:
                    yield Token('GT', '>', lineno)
            elif sym1 == '!':
                if sym2 == '=':
                    yield Token('NOTEQ', '!=', lineno)
                    idx += 1
                else:
                    yield Token('NOT', '!', lineno)
            elif sym1 == '&' and sym2 == '&':
                yield Token('AND', '&&', lineno)
                idx += 1
            elif sym1 == '|' and sym2 == '|':
                yield Token('OR', '||', lineno)
                idx += 1
            elif sym1 == '+':
                yield Token('PLUS', '+', lineno)
            elif sym1 == '-':
                yield Token('MINUS', '-', lineno)
            elif sym1 == '/':
                yield Token('DIVIDE', '/', lineno)
            elif sym1 == '*':
                yield Token('TIMES', '*', lineno)
            elif sym1 == '%':
                yield Token('MOD', '%', lineno)
            elif sym1 == '(':
                yield Token('LPAREN', '(', lineno)
            elif sym1 == ')':
                yield Token('RPAREN', ')', lineno)
            elif sym1 == '{':
                yield Token('BEGIN', '{', lineno)
            elif sym1 == '}':
                yield Token('END', '}', lineno)
            elif sym1 == ';':
                yield Token('SEMICOLON', ';', lineno)
            elif sym1 == ':':
                yield Token('COLON', ':', lineno)
            elif sym1 == ',':
                yield Token('COMMA', ',', lineno)
        elif state==State.COMMENT:
            if sym2 == '\n':
                state = State.START
        elif state==State.WORD:
            if sym1.isalpha() or sym1=='_' or  sym1.isdigit():
                accum += sym1
            else:
                kwd = {'true':'BOOLVAL','false':'BOOLVAL','print':'PRINT','println':'PRINTLN','int':'INT','bool':'BOOL','var':'VAR','fun':'FUN','if':'IF','else':'ELSE','while':'WHILE','return':'RETURN'}
                if accum in kwd:
                    yield Token(kwd[accum], accum, lineno)
                else:
                    yield Token('ID', accum, lineno)
                accum = ''
                idx -= 1
                state = State.START
        elif state==State.NUMBER:
            if sym1.isdigit():
                accum += sym1
            else:
                yield Token('INTVAL', accum, lineno)
                idx -= 1
                accum = ''
                state = State.START
        elif state==State.STRING:
            if sym1 != '"':
                accum += sym1
            else:
                yield Token('STRING', f'"{accum}"', lineno)
                accum = ''
                state = State.START
        idx += 1
    if state!=State.START:
        raise Exception('Lexical error: unexpected EOF')

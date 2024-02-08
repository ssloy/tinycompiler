class Token:
    def __init__(self, t, v, l=None):
        self.type, self.value, self.lineno = t, v, (l or 0) +1 # mwahaha, +1, sly, wtf? # TODO remove +1
        self.index, self.end = None, None # TODO needed for sly, remove in the future

    def __repr__(self):
         return f'Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno!r})'

class WendLexer:
    keywords    = {'true':'BOOLEAN','false':'BOOLEAN','print':'PRINT','println':'PRINT','int':'TYPE','bool':'TYPE','var':'VAR','fun':'FUN','if':'IF','else':'ELSE','while':'WHILE','return':'RETURN'}
    double_char = {'==':'COMP', '<=':'COMP', '>=':'COMP', '!=':'COMP', '&&':'AND', '||':'OR'}
    single_char = {'=':'ASSIGN','<':'COMP', '>':'COMP', '!':'NOT', '+':'PLUS', '-':'MINUS', '/':'DIVIDE', '*':'TIMES', '%':'MOD','(':'LPAREN',')':'RPAREN', '{':'BEGIN', '}':'END', ';':'SEMICOLON', ':':'COLON', ',':'COMMA'}
    tokens      = {'ID':'', 'STRING':'', 'INTEGER':''} | { v:'' for k, v in keywords.items() | double_char.items() | single_char.items() }

    def tokenize(self, text):
        lineno, idx, state, accum = 0, 0, 0, ''
        while idx<len(text):
            sym1 = text[idx+0] if idx<len(text)-0 else ' '
            sym2 = text[idx+1] if idx<len(text)-1 else ' '
            if state==0: # start scanning a new token
                if sym1 == '/' and sym2 == '/':   # start a comment scan
                    state = 1
                elif sym1.isalpha() or sym1=='_': # start a word scan
                    state = 3
                    accum += sym1
                elif sym1.isdigit():              # start a number scan
                    state = 4
                    accum += sym1
                elif sym1 == '"':                 # start a string scan
                    state = 2
                elif sym1 + sym2 in self.double_char:  # emit two-character token
                    yield Token(self.double_char[sym1+sym2], sym1+sym2, lineno)
                    idx += 1
                elif sym1 in self.single_char:         # emit one-character token
                    yield Token(self.single_char[sym1], sym1, lineno)
                elif sym1 not in ['\r', '\t', ' ', '\n']: # ignore whitespace
                    raise Exception(f'Lexical error: illegal character \'{sym1}\' at line {lineno}')
            elif state==3:                                          # scanning a word, check next character
                if sym1.isalpha() or sym1=='_' or  sym1.isdigit():  # still word?
                    accum += sym1                                   # if yes, continue
                else:                                               # otherwise the scan stops, we have a word
                    if accum in self.keywords:                           # is the word reserved?
                        yield Token(self.keywords[accum], accum, lineno) # if yes, keyword
                    else:
                        yield Token('ID', accum, lineno)            # identifier otherwise
                    idx -= 1
                    state, accum = 0, '' # start new scan
            elif state==4:                                          # scanning a number
                if sym1.isdigit():                                  # is next character a digit?
                    accum += sym1                                   # if yes, continue
                else:
                    yield Token('INTEGER', accum, lineno)            # otherwise, emit number token
                    idx -= 1
                    state, accum = 0, '' # start new scan
            elif state==2:                                          # scanning a string, check next character
                if sym1 != '"':                                     # if not quote mark,
                    accum += sym1                                   # continue the scan
                else:
                    yield Token('STRING', accum, lineno)            # otherwise emit the token
                    state, accum = 0, '' # start new scan
            if sym1 == '\n':
                lineno += 1
                if state==1: # if comment, start new scan
                    state,accum = 0, ''
            idx += 1
        if state!=0:
            raise Exception('Lexical error: unexpected EOF')

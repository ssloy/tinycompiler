class Token:
    def __init__(self, t, v, l=None):
        self.type, self.value, self.lineno = t, v, (l or 0)

    def __repr__(self):
         return f'Token(type={self.type!r}, value={self.value!r}, lineno={self.lineno!r})'

class WendLexer:
    keywords    = {'true':'BOOLEAN','false':'BOOLEAN','print':'PRINT','println':'PRINT','int':'TYPE','bool':'TYPE','if':'IF','else':'ELSE','while':'WHILE','return':'RETURN'}
    double_char = {'==':'COMP', '<=':'COMP', '>=':'COMP', '!=':'COMP', '&&':'AND', '||':'OR'}
    single_char = {'=':'ASSIGN','<':'COMP', '>':'COMP', '!':'NOT', '+':'PLUS', '-':'MINUS', '/':'DIVIDE', '*':'TIMES', '%':'MOD','(':'LPAREN',')':'RPAREN', '{':'BEGIN', '}':'END', ';':'SEMICOLON', ',':'COMMA'}
    tokens      = {'ID', 'STRING', 'INTEGER'} | { v for k, v in keywords.items() | double_char.items() | single_char.items() }

    def tokenize(self, text):
        lineno, idx, state, accum = 0, 0, 0, ''
        while idx<len(text):
            sym1,sym2 = (text+' ')[idx:idx+2]                                   # current character and the next one
            idx += 1
            if state==0:                                                        # start scanning a new token
                if sym1 == '/' and sym2 == '/':                                 # start a comment scan
                    state = 1
                elif sym1.isalpha() or sym1=='_':                               # start a word scan
                    state = 3
                elif sym1.isdigit():                                            # start a number scan
                    state = 4
                elif sym1 == '"':                                               # start a string scan
                    state = 2
                elif sym1 + sym2 in self.double_char:                           # emit a two-character token
                    yield Token(self.double_char[sym1+sym2], sym1+sym2, lineno)
                    idx += 1
                elif sym1 in self.single_char:                                  # emit a one-character token
                    yield Token(self.single_char[sym1], sym1, lineno)
                elif sym1 not in ['\r', '\t', ' ', '\n']:                       # ignore whitespace
                    raise Exception(f'Lexical error: illegal character \'{sym1}\' at line {lineno}')
            if state==2:                                                        # scanning a string
                accum += sym1
                if sym2 == '"' and (not accum or accum[-1]!='\\'):              # if not-escaped quote mark,
                    yield Token('STRING', accum[1:], lineno)                    # emit the token, do not forget to drop the opening quote
                    state, accum, idx = 0, '', idx+1                            # start a new scan, skip the ending quote
            elif state==3:                                                      # scanning a word
                accum += sym1
                if not (sym2.isalpha() or sym2=='_' or  sym2.isdigit()):        # still a word?
                    yield Token(self.keywords.get(accum, 'ID'), accum, lineno)  # if not, keyword or ID
                    state, accum = 0, ''                                        # start a new scan
            elif state==4:                                                      # scanning a number
                accum += sym1
                if not sym2.isdigit():                                          # is next character a digit?
                    yield Token('INTEGER', accum, lineno)                       # if not, emit number token
                    state, accum = 0, ''                                        # start a new scan
            if sym1 == '\n':
                lineno += 1
                if state==1:                                                    # if comment, start new scan
                    state, accum = 0, ''
        if state:
            raise Exception('Lexical error: unexpected EOF')

from sly import Lexer

class WendLexer(Lexer):
    tokens = { ID, BOOLVAL, INTVAL, STRING, PRINT, PRINTLN, INT, BOOL, VAR, FUN, IF, ELSE, WHILE, RETURN,
        PLUS, MINUS, TIMES, DIVIDE, MOD, LTEQ, LT, GTEQ, GT, EQ, NOTEQ, AND, OR, NOT,
        LPAREN, RPAREN, BEGIN, END, ASSIGN, SEMICOLON, COLON, COMMA }
    ignore = ' \t\r'
    ignore_comment = r'\/\/.*'

    ID        = r'[a-zA-Z_][a-zA-Z0-9_]*' # a regex per token (except for the remapped ones)
    INTVAL    = r'\d+'                    # N. B.: the order matters, first match will be taken
    PLUS      = r'\+'
    MINUS     = r'-'
    TIMES     = r'\*'
    DIVIDE    = r'/'
    MOD       = r'%'
    LTEQ      = r'<='
    LT        = r'<'
    GTEQ      = r'>='
    GT        = r'>'
    EQ        = r'=='
    NOTEQ     = r'!='
    AND       = r'\&\&'
    OR        = r'\|\|'
    NOT       = r'!'
    LPAREN    = r'\('
    RPAREN    = r'\)'
    BEGIN     = r'\{'
    END       = r'\}'
    ASSIGN    = r'='
    COLON     = r':'
    SEMICOLON = r';'
    COMMA     = r','
    STRING    = r'"[^"]*"'

    ID['true']    = BOOLVAL # token remapping for keywords
    ID['false']   = BOOLVAL # this is necessary because keywords match legal identifier pattern
    ID['print']   = PRINT
    ID['println'] = PRINTLN
    ID['int']     = INT
    ID['bool']    = BOOL
    ID['var']     = VAR
    ID['fun']     = FUN
    ID['if']      = IF
    ID['else']    = ELSE
    ID['while']   = WHILE
    ID['return']  = RETURN

    @_(r'\n+')
    def ignore_newline(self, t): # line number tracking
        self.lineno += len(t.value)

    def error(self, t):
        raise Exception('Line %d: illegal character %r' % (self.lineno, t.value[0]))

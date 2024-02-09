grammar = [('fun', ['FUN', 'ID', 'LPAREN', 'param_list', 'RPAREN', 'fun_type', 'BEGIN', 'var_list', 'fun_list', 'statement_list', 'END']),
    ('var', ['ID', 'COLON', 'TYPE']),
    ('param_list', ['param_list', 'COMMA', 'var']),
    ('param_list', ['var']),
    ('param_list', []),
    ('fun_type', ['COLON', 'TYPE']),
    ('fun_type', []),
    ('var_list', ['var_list', 'VAR', 'var', 'SEMICOLON']),
    ('var_list', []),
    ('fun_list', ['fun_list', 'fun']),
    ('fun_list', []),
    ('statement_list', ['statement_list', 'statement']),
    ('statement_list', []),
    ('statement', ['ID', 'LPAREN', 'arg_list', 'RPAREN', 'SEMICOLON']),
    ('statement', ['ID', 'ASSIGN', 'expr', 'SEMICOLON']),
    ('statement', ['RETURN', 'expr', 'SEMICOLON']),
    ('statement', ['RETURN', 'SEMICOLON']),
    ('statement', ['PRINT', 'expr', 'SEMICOLON']),
    ('statement', ['IF', 'expr', 'BEGIN', 'statement_list', 'END', 'else_statement']),
    ('statement', ['WHILE', 'expr', 'BEGIN', 'statement_list', 'END']),
    ('else_statement', ['ELSE', 'BEGIN', 'statement_list', 'END']),
    ('else_statement', []),
    ('arg_list', ['expr']),
    ('arg_list', ['arg_list', 'COMMA', 'expr']),
    ('arg_list', []),
    ('expr', ['conjunction']),
    ('expr', ['expr', 'OR', 'conjunction']),
    ('expr', ['STRING']),
    ('conjunction', ['literal']),
    ('conjunction', ['conjunction', 'AND', 'literal']),
    ('literal', ['comparand']),
    ('literal', ['NOT', 'comparand']),
    ('comparand', ['addend']),
    ('comparand', ['addend', 'COMP', 'addend']),
    ('addend', ['term']),
    ('addend', ['addend', 'MINUS', 'term']),
    ('addend', ['addend', 'PLUS', 'term']),
    ('term', ['factor']),
    ('term', ['term', 'MOD', 'factor']),
    ('term', ['term', 'DIVIDE', 'factor']),
    ('term', ['term', 'TIMES', 'factor']),
    ('factor', ['atom']),
    ('factor', ['PLUS', 'atom']),
    ('factor', ['MINUS', 'atom']),
    ('atom', ['BOOLEAN']),
    ('atom', ['INTEGER']),
    ('atom', ['ID', 'LPAREN', 'arg_list', 'RPAREN']),
    ('atom', ['ID']),
    ('atom', ['LPAREN', 'expr', 'RPAREN'])]

tokens = ['AND', 'ASSIGN', 'BEGIN', 'BOOLEAN', 'COLON', 'COMMA', 'COMP', 'DIVIDE', 'ELSE', 'END', 'FUN', 'ID', 'IF', 'INTEGER', 'LPAREN', 'MINUS', 'MOD', 'NOT', 'OR', 'PLUS', 'PRINT', 'RETURN', 'RPAREN', 'SEMICOLON', 'STRING', 'TIMES', 'TYPE', 'VAR', 'WHILE']


class EarleyItem:
    def __init__(self, index_of_rule_in_grammar, index_of_symbol_in_rule, start_position_in_input, prev_item = None):
        self.rule, self.next, self.start, self.prev = index_of_rule_in_grammar, index_of_symbol_in_rule, start_position_in_input, prev_item

    def __repr__(self):
        lhs, rhs = grammar[self.rule]
        return "({}, {} → {})".format(self.start, lhs or '⊤', ' '.join(rhs[:self.next] + ['∘'] + rhs[self.next:]))

    def next_symbol(self):
        return grammar[self.rule][1][self.next] if self.next<len(grammar[self.rule][1]) else None

    def advance(self):
        return EarleyItem(self.rule, self.next+1, self.start, self)

    def __eq__(self, other):
        return self.rule == other.rule and self.next == other.next and self.start == other.start #NB no self.prev

tokenize = iter('FUN ID LPAREN RPAREN BEGIN PRINT INTEGER PLUS INTEGER TIMES INTEGER SEMICOLON END'.split(' '))
#tokenize = iter('INTEGER PLUS INTEGER TIMES INTEGER'.split(' '))

S = [[EarleyItem(0, 0, 0)]]
i = 0
while True:
    token = next(tokenize, None)
    j = 0
    while j < len(S[i]):
        symbol = S[i][j].next_symbol()
        if symbol is None:     # complete
            for item in S[S[i][j].start]:
                if item.next_symbol() == grammar[S[i][j].rule][0]:
                    if item.advance() not in S[i]:
                        S[i].append(item.advance())
                        S[i][-1].prev = S[i][j]
        elif symbol in tokens: # scan
            if symbol == token:
                if len(S)==i+1: S.append([])
                S[i+1].append(S[i][j].advance())
#                S[i+1][-1].prev = S[i][j]
        else:                  # predict
            for idx, (lhs, rhs) in enumerate(grammar):
                if lhs == symbol:
                    newitem = EarleyItem(idx, 0, i, S[i][j])
                    if newitem not in S[i]:
                        S[i].append(newitem)
        j += 1
    i += 1
    if token is None or len(S)==i: break

#print('\n')
#print(border_msg('Earley charts'))
#for _ in S:
#    print(_)

print()
prev = next((_ for _ in S[-1] if _ == EarleyItem(0,len(grammar[0][1]),0)), None)
while prev:
    if prev.next_symbol() is None:
        print(prev)
    prev = prev.prev


grammar = [
    (None, ['fun']), # None is the start symbol of the grammar
    ('fun', ['FUN', 'ID', 'LPAREN', 'param_list', 'RPAREN', 'fun_type', 'BEGIN', 'var_list', 'fun_list', 'statement_list', 'END']),
    ('param_list', []),
    ('param_list', ['var']),
    ('param_list', ['param_list', 'COMMA', 'var']),
    ('var_list', []),
    ('var_list', ['var_list', 'VAR', 'var', 'SEMICOLON']),
    ('var', ['ID', 'COLON', 'TYPE']),
    ('fun_list', []),
    ('fun_list', ['fun_list', 'fun']),
    ('statement_list', []),
    ('statement_list', ['statement_list', 'statement']),
    ('statement', ['ID', 'LPAREN', 'arg_list', 'RPAREN', 'SEMICOLON']),
    ('statement', ['ID', 'ASSIGN', 'expr', 'SEMICOLON']),
    ('statement', ['RETURN', 'expr', 'SEMICOLON']),
    ('statement', ['RETURN', 'SEMICOLON']),
    ('statement', ['PRINT', 'expr', 'SEMICOLON']),
    ('statement', ['IF', 'expr', 'BEGIN', 'statement_list', 'END', 'else_statement']),
    ('statement', ['WHILE', 'expr', 'BEGIN', 'statement_list', 'END']),
    ('else_statement', []),
    ('else_statement', ['ELSE', 'BEGIN', 'statement_list', 'END']),
    ('expr', ['BOOLVAL']),
    ('expr', ['INTVAL']),
    ('expr', ['STRING']),
    ('expr', ['ID', 'LPAREN', 'arg_list', 'RPAREN']),
    ('expr', ['ID']),
    ('expr', ['NOT', 'expr']),
    ('expr', ['expr', 'OR', 'expr']),
    ('expr', ['expr', 'AND', 'expr']),
    ('expr', ['expr', 'COMP', 'expr']),
    ('expr', ['expr', 'MOD', 'expr']),
    ('expr', ['expr', 'DIVIDE', 'expr']),
    ('expr', ['expr', 'TIMES', 'expr']),
    ('expr', ['expr', 'MINUS', 'expr']),
    ('expr', ['expr', 'PLUS', 'expr']),
    ('expr', ['LPAREN', 'expr', 'RPAREN']),
    ('expr', ['PLUS', 'expr']),
    ('expr', ['MINUS', 'expr']),
    ('arg_list', []),
    ('arg_list', ['expr']),
    ('arg_list', ['arg_list', 'COMMA', 'expr']),
    ('fun_type', []),
    ('fun_type', ['COLON', 'TYPE'])
    ]
grammar = [
    (None, ['expr']), # None is the start symbol of the grammar
    ('expr', ['INTVAL']),
    ('expr', ['expr', 'TIMES', 'expr']),
    ('expr', ['expr', 'PLUS', 'expr']),
    ]

tokens = ['AND', 'ASSIGN', 'BEGIN', 'BOOLVAL', 'COLON', 'COMMA', 'COMP', 'DIVIDE', 'ELSE', 'END', 'FUN', 'ID', 'IF', 'INTVAL', 'LPAREN', 'MINUS', 'MOD', 'NOT', 'OR', 'PLUS', 'PRINT', 'RETURN', 'RPAREN', 'SEMICOLON', 'STRING', 'TIMES', 'TYPE', 'VAR', 'WHILE']

def border_msg(msg):
    row = len(msg) + 2
    h = ''.join(['+'] + ['-' *row] + ['+'])
    result= h + '\n'"| "+msg+" |"'\n' + h
    return result

print(border_msg('Grammar'))
for lhs, rhs in grammar:
    print("{} → {}".format(lhs or '⊤', " ".join(rhs)))


def nullable(): # set of all nonterminals that can be empty
    nullable = { lhs for lhs,rhs in grammar if not rhs } # directly empty production rules
    prev = None
    while prev != len(nullable): # indirectly empty, add nonterminals until convergence
        prev = len(nullable)
        nullable |= { lhs for lhs,rhs in grammar if all(x in nullable for x in rhs) }
    return nullable
nullable = nullable()
print('\n')
print(border_msg('nullable nonterminals'))
print(nullable)


class EarleyItem:
    def __init__(self, index_of_rule_in_grammar, index_of_symbol_in_rule, start_position_in_input):
        self.rule, self.next, self.start = index_of_rule_in_grammar, index_of_symbol_in_rule, start_position_in_input

    def __repr__(self):
        lhs, rhs = grammar[self.rule]
        return "({}, {} → {})".format(self.start, lhs or '⊤', ' '.join(rhs[:self.next] + ['∘'] + rhs[self.next:]))

    def next_symbol(self):
        return grammar[self.rule][1][self.next] if self.next<len(grammar[self.rule][1]) else None

    def __eq__(self, other):
        return self.rule == other.rule and self.next == other.next and self.start == other.start

#tokenize = iter('FUN ID LPAREN RPAREN BEGIN PRINT INTVAL PLUS INTVAL TIMES INTVAL SEMICOLON END'.split(' '))
tokenize = iter('INTVAL PLUS INTVAL TIMES INTVAL'.split(' '))

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
                    newitem = EarleyItem(item.rule, item.next+1, item.start)
                    if newitem not in S[i]:
                        S[i].append(newitem)
        elif symbol in tokens: # scan
            if symbol == token:
                if len(S)==i+1: S.append([])
                S[i+1].append(EarleyItem(S[i][j].rule, S[i][j].next+1, S[i][j].start))
        else:                  # predict
            for idx, (lhs, rhs) in enumerate(grammar):
                if lhs == symbol:
                    newitem = EarleyItem(idx, 0, i)
                    if newitem not in S[i]:
                        S[i].append(newitem)
                    if lhs in nullable: # Aycock and Horspool (2002): when performing a prediction, if the predicted symbol is nullable, then advance the predictor one step.
                        newitem = EarleyItem(S[i][j].rule, S[i][j].next+1, S[i][j].start)
                        if newitem not in S[i]:
                            S[i].append(newitem)
        j += 1
    i += 1
    if token is None or len(S)==i: break

print('\n')
print(border_msg('Earley charts'))
for _ in S:
    print(_)


'''

def first(): # for each nonterminal, compute a set of all the terminals it can start from
    first = { lhs:set() for lhs, rhs in grammar }
    size = lambda d : sum(len(_) for _ in d.values())
    prev = None
    while prev != size(first): # add terminals until convergence
        prev = size(first)
        for lhs, rhs in grammar:
            for sym in rhs: # iterate through the rule until non-nullable symbol is found
                first[lhs] |= { sym } if sym in tokens else first[sym]
                if sym not in nullable: break
    return first
first = first()
print('\n')
print(border_msg('First terminals'))
for lhs in first.keys():
    if len(first[lhs])>1:
        print('{} → ( {} ) ...'.format(lhs or '⊤', " | ".join(first[lhs])))
    else:
        print('{} → {} ...'.format(lhs or '⊤', *list(first[lhs])))

def follow(): # for each nonterminal, compute a set of terminals that can immediately follow that nonterminal
    follow = { lhs:set() for lhs, rhs in grammar }
    size = lambda d : sum(len(_) for _ in d.values())
    prev = None
    while prev != size(first): # add terminals until convergence
        prev = size(first)
        for lhs, rhs in grammar:
            for i,p in enumerate(rhs):
                if p in tokens: continue # for every nonterminal in the production rules
                for q in rhs[i+1:]: # iterate through the rest of the rule until non-nullable symbol is found
                    follow[p] |= { q } if q in tokens else first[q]
                    if q not in nullable: break
            if len(rhs) and rhs[-1] not in tokens:
                follow[rhs[-1]] |= follow[lhs]
    return follow
print('\n')
print(border_msg('Follow terminals'))
follow = follow()
for lhs in follow.keys():
    if len(follow[lhs])>1:
        print('{} ( {} ) ...'.format(lhs or '⊤', " | ".join(follow[lhs])))
    elif len(follow[lhs]):
        print('{} {} ...'.format(lhs or '⊤', *list(follow[lhs])))
    else:
        print('{} {}'.format(lhs or '⊤', u'\u2205'))

#print(follow)


#def print_item(prefix, rule, index):
#    lhs, rhs = grammar[rule]
#    print("{}{} → {}".format(prefix, lhs or '⊤',
#        " ".join(rhs[:index] + ['∘'] + rhs[index:])))


'''



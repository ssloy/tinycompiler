grammar = [
    (None, ['fun']),
    ('fun', ['FUN', 'ID', 'LPAREN', 'param_list', 'RPAREN', 'fun_type', 'BEGIN', 'var_list', 'fun_list', 'statement_list', 'END']),
    ('param_list', ['var']),
    ('param_list', []),
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
    ('else_statement', ['ELSE', 'BEGIN', 'statement_list', 'END']),
    ('else_statement', []),
    ('expr', ['BOOLVAL']),
    ('expr', ['INTVAL']),
    ('expr', ['STRING']),
    ('expr', ['ID', 'LPAREN', 'arg_list', 'RPAREN']),
    ('expr', ['ID']),
    ('expr', ['NOT', 'expr']),
#   ('expr', ['expr', 'OR', 'expr']),
#   ('expr', ['expr', 'AND', 'expr']),
#   ('expr', ['expr', 'COMP', 'expr']),
#   ('expr', ['expr', 'MOD', 'expr']),
#   ('expr', ['expr', 'DIVIDE', 'expr']),
#   ('expr', ['expr', 'TIMES', 'expr']),
#   ('expr', ['expr', 'MINUS', 'expr']),
#   ('expr', ['expr', 'PLUS', 'expr']),
    ('expr', ['LPAREN', 'expr', 'RPAREN']),
#   ('expr', ['PLUS', 'expr']),
#   ('expr', ['MINUS', 'expr']),
    ('arg_list', ['expr']),
    ('arg_list', []),
    ('arg_list', ['arg_list', 'COMMA', 'expr']),
    ('fun_type', []),
    ('fun_type', ['COLON', 'TYPE'])
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

def empty(): # set of all nonterminals that can be empty
    empty = { lhs for lhs,rhs in grammar if not rhs } # directly empty production rules
    prev = None
    while prev != len(empty): # indirectly empty, add nonterminals until convergence
        prev = len(empty)
        empty |= { lhs for lhs,rhs in grammar if all(x in empty for x in rhs) }
    return empty
empty = empty()
print('\n')
print(border_msg('Empty nonterminals'))
print(empty)

def first(): # for each nonterminal, compute a set of all the terminals it can start from
    first = { lhs:set() for lhs, rhs in grammar }
    size = lambda d : sum(len(_) for _ in d.values())
    prev = None
    while prev != size(first): # add terminals until convergence
        prev = size(first)
        for lhs, rhs in grammar:
            for sym in rhs: # iterate through the rule until non-empty symbol is found
                first[lhs] |= { sym } if sym in tokens else first[sym]
                if sym not in empty: break
    return first
first = first()
print('\n')
print(border_msg('First terminals'))
for lhs in first.keys():
    print('{} → ( {} ) ...'.format(lhs or '⊤', " | ".join(first[lhs])))

def follow(): # for each nonterminal, compute a set of terminals that can immediately follow that nonterminal
    follow = { lhs:set() for lhs, rhs in grammar }
    size = lambda d : sum(len(_) for _ in d.values())
    prev = None
    while prev != size(first): # add terminals until convergence
        prev = size(first)
        for lhs, rhs in grammar:
            for i,p in enumerate(rhs):
                if p in tokens: continue # for every nonterminal in the production rules
                for q in rhs[i+1:]: # iterate through the rest of the rule until non-empty symbol is found
                    follow[p] |= { q } if q in tokens else first[q]
                    if q not in empty: break
            if len(rhs) and rhs[-1] not in tokens:
                follow[rhs[-1]] |= follow[lhs]
    return follow
print('\n')
print(border_msg('Follow terminals'))
follow = follow()
for lhs in follow.keys():
    print('{} ( {} ) ...'.format(lhs or '⊤', " | ".join(follow[lhs])))

#print(follow)


#def print_item(prefix, rule, index):
#    lhs, rhs = grammar[rule]
#    print("{}{} → {}".format(prefix, lhs or '⊤',
#        " ".join(rhs[:index] + ['∘'] + rhs[index:])))



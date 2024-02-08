grammar = '''fun ::= FUN ID LPAREN param_list RPAREN fun_type BEGIN var_list fun_list statement_list END
             var ::= ID COLON TYPE
      param_list ::= param_list COMMA var|var|
        fun_type ::= COLON TYPE|
        var_list ::= var_list VAR var SEMICOLON|
        fun_list ::= fun_list fun|
  statement_list ::= statement_list statement|
       statement ::= ID LPAREN arg_list RPAREN SEMICOLON|ID ASSIGN expr SEMICOLON|RETURN expr SEMICOLON|RETURN SEMICOLON|PRINT expr SEMICOLON|IF expr BEGIN statement_list END else_statement|WHILE expr BEGIN statement_list END
  else_statement ::= ELSE BEGIN statement_list END|
        arg_list ::= expr|arg_list COMMA expr|
            expr ::= conjunction|expr OR conjunction|STRING
     conjunction ::= literal|conjunction AND literal
         literal ::= comparand|NOT comparand
       comparand ::= addend|addend COMP addend
          addend ::= term|addend MINUS term|addend PLUS term
            term ::= factor|term MOD factor|term DIVIDE factor|term TIMES factor
          factor ::= atom|PLUS atom|MINUS atom
            atom ::= BOOLEAN|INTEGER|ID LPAREN arg_list RPAREN|ID|LPAREN expr RPAREN'''

grammar = [ (rule.split('::=')[0].strip(), [x for x in production.split(' ') if x!='']) for rule in grammar.split('\n') for production in rule.split('::=')[1].strip().split('|') ]
print(grammar)

tokens = ['AND', 'ASSIGN', 'BEGIN', 'BOOLEAN', 'COLON', 'COMMA', 'COMP', 'DIVIDE', 'ELSE', 'END', 'FUN', 'ID', 'IF', 'INTEGER', 'LPAREN', 'MINUS', 'MOD', 'NOT', 'OR', 'PLUS', 'PRINT', 'RETURN', 'RPAREN', 'SEMICOLON', 'STRING', 'TIMES', 'TYPE', 'VAR', 'WHILE']

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
#                   if lhs in nullable: # Aycock and Horspool (2002): when performing a prediction, if the predicted symbol is nullable, then advance the predictor one step.
#                       if S[i][j].advance() not in S[i]:
#                           S[i].append(S[i][j].advance())
#                           S[i][-1].prev = S[i][S[i].index(newitem)]
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




'''
S -> FUN.
FUN -> fun id lparen PARAM_LIST rparen FUN_TYPE begin VAR_LIST FUN_LIST STATEMENT_LIST end.
VAR -> id colon type.
PARAM_LIST -> PARAM_LIST comma VAR|VAR|.
FUN_TYPE -> colon type|.
VAR_LIST -> VAR_LIST var VAR semicolon|.
FUN_LIST -> FUN_LIST FUN|.
STATEMENT_LIST -> STATEMENT_LIST STATEMENT|.
STATEMENT -> id lparen ARG_LIST rparen semicolon|id assign EXPR semicolon|return EXPR semicolon|return semicolon|print EXPR semicolon|if EXPR begin STATEMENT_LIST end ELSE_STATEMENT|while EXPR begin STATEMENT_LIST end.
ELSE_STATEMENT -> else begin STATEMENT_LIST end|.
ARG_LIST -> EXPR|ARG_LIST comma EXPR|.
EXPR -> CONJUNCTION|EXPR or CONJUNCTION|string.
CONJUNCTION -> LITERAL|CONJUNCTION and LITERAL.
LITERAL -> COMPARAND|not COMPARAND.
COMPARAND -> ADDEND|ADDEND comp ADDEND.
ADDEND -> TERM|ADDEND minus TERM|ADDEND plus TERM.
TERM -> FACTOR|TERM mod FACTOR|TERM divide FACTOR|TERM times FACTOR.
FACTOR -> ATOM|plus ATOM|minus ATOM.
ATOM -> BOOLEAN|INTEGER|id lparen ARG_LIST rparen|id|lparen EXPR rparen.
'''

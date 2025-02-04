from lexer import WendLexer
from syntree import *

class ParseState:
    def __init__(self, rule, dot, start, token = None, prev = None):
        self.rule  = rule  # index of the parse rule in the grammar
        self.dot   = dot   # index of next symbol in the rule (dot position)
        self.start = start # we saw this many tokens when we started the rule
        self.token = token # we saw this many tokens up to the current dot position   # these two members are not necessary for
        self.prev  = prev  # parent parse state pointer                               # the recogninzer, but are handy to retrieve a parse path

    def next_symbol(self):
        prod = WendParser.grammar[self.rule][1]
        return prod[self.dot] if self.dot<len(prod) else None

    def __eq__(self, other):
        return self.rule == other.rule and self.dot == other.dot and self.start == other.start # NB no self.token, no self.prev

class WendParser: # the grammar is a list of triplets [nonterminal, production rule, AST node constructor]
    grammar = [['fun',            ['fun_type', 'ID', 'LPAREN', 'param_list', 'RPAREN', 'BEGIN', 'var_list', 'fun_list', 'statement_list', 'END'],
                                                                                                      lambda p: Function(p[1].value, p[3], p[6], p[7], p[8], {'type':p[0], 'lineno':p[1].lineno})],
               ['var',            ['TYPE', 'ID'],                                                     lambda p: (p[1].value, Type.INT if p[0].value=='int' else Type.BOOL)],
               ['param_list',     ['var'],                                                            lambda p: p],
               ['param_list',     [],                                                                 lambda p: p],
               ['param_list',     ['param_list', 'COMMA', 'var'],                                     lambda p: p[0] + [ p[2] ]],
               ['fun_type',       ['TYPE'],                                                           lambda p: Type.INT if p[0].value=='int' else Type.BOOL],
               ['fun_type',       [],                                                                 lambda p: Type.VOID],
               ['var_list',       ['var_list', 'var', 'SEMICOLON'],                                   lambda p: p[0] + [ p[1] ]],
               ['var_list',       [],                                                                 lambda p: p],
               ['fun_list',       ['fun_list', 'fun'],                                                lambda p: p[0] + [ p[1] ]],
               ['fun_list',       [],                                                                 lambda p: p],
               ['statement_list', ['statement_list', 'statement'],                                    lambda p: p[0] + [ p[1] ]],
               ['statement_list', [],                                                                 lambda p: p],
               ['statement',      ['ID', 'LPAREN', 'arg_list', 'RPAREN', 'SEMICOLON'],                lambda p: FunCall(p[0].value, p[2], {'lineno':p[0].lineno})],
               ['statement',      ['ID', 'ASSIGN', 'expr', 'SEMICOLON'],                              lambda p: Assign(p[0].value, p[2], {'lineno':p[0].lineno})],
               ['statement',      ['RETURN', 'expr', 'SEMICOLON'],                                    lambda p: Return(p[1], {'lineno':p[0].lineno})],
               ['statement',      ['RETURN', 'SEMICOLON'],                                            lambda p: Return(None, {'lineno':p[0].lineno})],
               ['statement',      ['PRINT', 'expr', 'SEMICOLON'],                                     lambda p: Print(p[1], p[0].value=='println', {'lineno':p[0].lineno})],
               ['statement',      ['IF', 'expr', 'BEGIN', 'statement_list', 'END', 'else_statement'], lambda p: IfThenElse(p[1], p[3], p[5], {'lineno':p[0].lineno})],
               ['else_statement', ['ELSE', 'BEGIN', 'statement_list', 'END'],                         lambda p: p[2]],
               ['else_statement', [],                                                                 lambda p: p],
               ['statement',      ['WHILE', 'expr', 'BEGIN', 'statement_list', 'END'],                lambda p: While(p[1], p[3], {'lineno':p[0].lineno})],
               ['arg_list',       ['expr'],                                                           lambda p: p],
               ['arg_list',       ['arg_list', 'COMMA', 'expr'],                                      lambda p: p[0] + [ p[2] ]],
               ['arg_list',       [],                                                                 lambda p: p],
               ['expr',           ['conjunction'],                                                    lambda p: p[0]],
               ['expr',           ['expr', 'OR', 'conjunction'],                                      lambda p: LogicOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['expr',           ['STRING'],                                                         lambda p: String(p[0].value, {'lineno':p[0].lineno})],
               ['conjunction',    ['literal'],                                                        lambda p: p[0]],
               ['conjunction',    ['conjunction', 'AND', 'literal'],                                  lambda p: LogicOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['literal',        ['comparand'],                                                      lambda p: p[0]],
               ['literal',        ['NOT', 'comparand'],                                               lambda p: LogicOp('==', Boolean(False, {}), p[1], {'lineno':p[0].lineno})],
               ['comparand',      ['addend'],                                                         lambda p: p[0]],
               ['comparand',      ['addend', 'COMP', 'addend'],                                       lambda p: LogicOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['addend',         ['term'],                                                           lambda p: p[0]],
               ['addend',         ['addend', 'MINUS', 'term'],                                        lambda p: ArithOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['addend',         ['addend', 'PLUS', 'term'],                                         lambda p: ArithOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['term',           ['factor'],                                                         lambda p: p[0]],
               ['term',           ['term', 'MOD', 'factor'],                                          lambda p: ArithOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['term',           ['term', 'DIVIDE', 'factor'],                                       lambda p: ArithOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['term',           ['term', 'TIMES', 'factor'],                                        lambda p: ArithOp(p[1].value, p[0], p[2], {'lineno':p[1].lineno})],
               ['factor',         ['atom'],                                                           lambda p: p[0]],
               ['factor',         ['PLUS', 'atom'],                                                   lambda p: p[1]],
               ['factor',         ['MINUS', 'atom'],                                                  lambda p: ArithOp('-', Integer(0, {}), p[1], {'lineno':p[0].lineno})],
               ['atom',           ['BOOLEAN'],                                                        lambda p: Boolean(p[0].value=='true', {'lineno':p[0].lineno})],
               ['atom',           ['INTEGER'],                                                        lambda p: Integer(int(p[0].value), {'lineno':p[0].lineno})],
               ['atom',           ['ID', 'LPAREN', 'arg_list', 'RPAREN'],                             lambda p: FunCall(p[0].value, p[2], {'lineno':p[0].lineno})],
               ['atom',           ['ID'],                                                             lambda p: Var(p[0].value, {'lineno':p[0].lineno})],
               ['atom',           ['LPAREN', 'expr', 'RPAREN'],                                       lambda p: p[1]]]

    def recognize(self, tokens): # check the syntax
        charts, self.seen = [[ParseState(0,0,0)]], []

        def append(i, state):
            if len(charts)==i: charts.append([])
            if state not in charts[i]: charts[i].append(state)

        while not self.seen or self.seen[-1]:    # fetch tokens one by one until end of file
            self.seen.append(next(tokens, None)) # keep all the tokens we encounter
            pos = len(self.seen)-1
            i = 0
            while i < len(charts[pos]):          # iterate through all Earley items in current chart
                state  = charts[pos][i]
                symbol = state.next_symbol()     # next symbol in the production rule
                if symbol is None:               # if no symbol: completed state
                    for item in charts[state.start]:
                        if item.next_symbol() == self.grammar[state.rule][0]:
                            append(pos, ParseState(item.rule, item.dot+1, item.start, pos, state))
                elif symbol in WendLexer.tokens: # if next symbol is a terminal,
                    if self.seen[-1] and symbol == self.seen[-1].type:  # scan a token
                        append(pos+1, ParseState(state.rule, state.dot+1, state.start, pos+1, state))
                else:                            # if next symbol is nonterminal, emit a prediction state
                    for idx, (lhs, rhs, _) in enumerate(self.grammar):
                        if lhs == symbol:
                            append(pos, ParseState(idx, 0, pos, pos, state))
                i += 1
            if self.seen[-1] and len(charts)==pos+1:
                raise Exception(f'Syntax error at line {self.seen[-1].lineno}, token={self.seen[-1].type}')
        cur = [ state for state in charts[-1] if state == ParseState(0, len(self.grammar[0][1]), 0) ] # all completed states at the end of the parse
        if not cur: # no final production rule found
            raise Exception('Syntax error: unexpected EOF')
        return cur[0]

    def build_syntree(self, rule):         # recover a parse path and build the syntax tree
        production = []                    # the production sequence:
        while rule:                        # rewind through the charts
            if rule.next_symbol() is None: # keep completed rules only
                production.append(rule)
            rule = rule.prev

        stack, token = [], 0               # now apply production rules in order: build a stack from the input rules
        for rule in reversed(production):  # chomp and chew then according to the production rules, put one symbol back after each chomp
            stack += self.seen[token:rule.token]
            token = rule.token
            chomp = len(self.grammar[rule.rule][1])        # number of symbols in the production rule
            chew  = []
            if chomp>0:                                    # chomp those symbols from the stack
                chew = stack[-chomp:]
                del stack[-chomp:]
            stack.append(self.grammar[rule.rule][2](chew)) # put AST node back on the stack
        return stack[0] # normally we have only one symbol left on the stack

    def parse(self, tokens):
        return self.build_syntree( self.recognize(tokens) )

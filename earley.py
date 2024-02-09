from lexer import WendLexer
from syntree import *

class State:
    def __init__(self, index_of_rule_in_grammar, index_of_symbol_in_rule, start_position_in_input, cur_pos = None, prev_item = None):
        self.rule, self.next, self.start, self.cur, self.prev = index_of_rule_in_grammar, index_of_symbol_in_rule, start_position_in_input, cur_pos, prev_item

    def __repr__(self):
        lhs, rhs, _ = WendParser.grammar[self.rule]
        return "({}:{}, {} → {})".format(self.start, self.cur, lhs or '⊤', ' '.join(rhs[:self.next] + ['∘'] + rhs[self.next:]))

    def next_symbol(self):
        return WendParser.grammar[self.rule][1][self.next] if self.next<len(WendParser.grammar[self.rule][1]) else None

    def __eq__(self, other):
        return self.rule == other.rule and self.next == other.next and self.start == other.start # NB no self.prev, no self.cur

def append(charts, i, state):
    if len(charts)==i: charts.append([])
    if state not in charts[i]: charts[i].append(state)

class WendParser:
    grammar = [['fun',            ['FUN', 'ID', 'LPAREN', 'param_list', 'RPAREN', 'fun_type', 'BEGIN', 'var_list', 'fun_list', 'statement_list', 'END'],
                                                                                                      lambda p: Function(p[1].value, p[3], p[7], p[8], p[9], {'type':p[5], 'lineno':p[0].lineno})],
               ['var',            ['ID', 'COLON', 'TYPE'],                                            lambda p: (p[0].value, {'type':Type.INT if p[2].value=='int' else Type.BOOL, 'lineno':p[0].lineno})],
               ['param_list',     ['var'],                                                            lambda p: p],
               ['param_list',     [],                                                                 lambda p: p],
               ['param_list',     ['param_list', 'COMMA', 'var'],                                     lambda p: p[0] + [ p[2] ]],
               ['fun_type',       ['COLON', 'TYPE'],                                                  lambda p: Type.INT if p[1].value=='int' else Type.BOOL],
               ['fun_type',       [],                                                                 lambda p: Type.VOID],
               ['var_list',       ['var_list', 'VAR', 'var', 'SEMICOLON'],                            lambda p: p[0] + [ p[2] ]],
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
               ['literal',        ['NOT', 'comparand'],                                               lambda p: LogicOp('==', Boolean(False), p[1], {'lineno':p[0].lineno})],
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
               ['factor',         ['MINUS', 'atom'],                                                  lambda p: ArithOp('-', Integer(0), p[1], {'lineno':p[0].lineno})],
               ['atom',           ['BOOLEAN'],                                                        lambda p: Boolean(p[0].value=='true', {'lineno':p[0].lineno})],
               ['atom',           ['INTEGER'],                                                        lambda p: Integer(int(p[0].value), {'lineno':p[0].lineno})],
               ['atom',           ['ID', 'LPAREN', 'arg_list', 'RPAREN'],                             lambda p: FunCall(p[0].value, p[2], {'lineno':p[0].lineno})],
               ['atom',           ['ID'],                                                             lambda p: Var(p[0].value, {'lineno':p[0].lineno})],
               ['atom',           ['LPAREN', 'expr', 'RPAREN'],                                       lambda p: p[1]]]

    def parse(self, tokens):
        charts, seen = [[State(0,0,0)]], []
        while not seen or seen[-1]:          # until end of file
            seen.append(next(tokens, None))  # keep all the tokens we encounter
            pos, j = len(seen)-1, 0
            while j < len(charts[pos]):      # iterate through all Earley items in current chart
                state = charts[pos][j]
                symbol = state.next_symbol() # next symbol in the production rule
                if symbol is None:           # if no symbol: completed state
                    for item in charts[state.start]:
                        if item.next_symbol() == self.grammar[state.rule][0]:
                            append(charts, pos, State(item.rule, item.next+1, item.start, pos, state))
                elif symbol in WendLexer.tokens: # if next symbol is a terminal,
                    if symbol == seen[-1].type:  # scan a token
                        append(charts, pos+1, State(state.rule, state.next+1, state.start, pos+1, state))
                else:                            # if next symbol is non-terminal, emit a prediction state
                    for idx, (lhs, rhs, _) in enumerate(self.grammar):
                        if lhs == symbol:        # N. B.: it is possible to check whether the lookahead is in the "first" set to avoid emitting spurious predictions, but I do not care
                            append(charts, pos, State(idx, 0, pos, pos, state))
                j += 1
            if seen[-1] and len(charts)==pos+1:
                raise Exception(f'Syntax error at line {seen[-1].lineno}, token={seen[-1].type}')

        cur = None
        for state in charts[-1]: # find the final production rule
            if state == State(0, len(self.grammar[0][1]), 0):
                cur = state

        production = [] # find the parse path
        while cur: # rewind through the charts
            if cur.next_symbol() is None: # keep completed rules only
                production.append(cur)
            cur = cur.prev

        stack = []
        pos = 0
        for rule in reversed(production):
            stack = stack + seen[pos:rule.cur]
            pos = rule.cur
            nsym = len(self.grammar[rule.rule][1])
            chew = []
            if nsym>0: # chomp symbols from the stack
                chew = stack[-nsym:]
                del stack[-nsym:]
            stack.append(self.grammar[rule.rule][2](chew)) # put one symbol back on the stack
        return stack[0] # normally we have only one symbol on the stack

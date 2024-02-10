from syntree import *
from symtable import *

class LabelFactory: # this is a suffix to add to all function names
    counter = 0     # in particular, it is useful for function overloading
    @staticmethod   # it is also useful for different goto labels (loops, conditional statements etc) in assembly code
    def new_label():
        LabelFactory.counter += 1
        return "uniqstr%d" % LabelFactory.counter

def build_symtable(ast):
    if not isinstance(ast, Function) or ast.name != 'main' or ast.deco['type'] != Type.VOID or len(ast.args)>0:
        raise Exception('Cannot find a valid entry point')
    symtable = SymbolTable()
    symtable.add_fun(ast.name, [], ast.deco)
    ast.deco['label']   = ast.name + '_' + LabelFactory.new_label() # unique label
    ast.deco['strings'] = [] # collection of constant strings from the program
    process_scope(ast, symtable)
    ast.deco['scope_cnt'] = symtable.scope_cnt # total number of functions, necessary for the static scope display table allocation

def process_scope(fun, symtable):
    fun.deco['local'] = []       # set of local variable names: len*4 is the memory necessary on the stack, the names are here to be put in comments
    symtable.push_scope(fun.deco)
    for v in fun.args: # process function arguments
        symtable.add_var(*v)
    for v in fun.var:  # process local variables
        symtable.add_var(*v)
        fun.deco['local'].append(v[0])
    for f in fun.fun:  # process nested functions: first add function symbols to the table
        symtable.add_fun(f.name, [d['type'] for v,d in f.args], f.deco)
        f.deco['label'] = f.name + '_' + LabelFactory.new_label() # still need unique labels
    for f in fun.fun:  # then process nested function bodies
        process_scope(f, symtable)
    for s in fun.body: # process the list of statements
        process_stat(s, symtable)
    symtable.pop_scope()

def process_stat(n, symtable): # process "statement" syntax tree nodes
    match n:
        case Print(): # no type checking is necessary
            process_expr(n.expr, symtable)
        case Return():
            if n.expr is None: return
            process_expr(n.expr, symtable)
            if symtable.ret_stack[-1]['type'] != n.expr.deco['type']:
                raise Exception('Incompatible types in return statement, line %s', n.deco['lineno'])
        case Assign():
            process_expr(n.expr, symtable)
            deco = symtable.find_var(n.name)
            n.deco |= { 'scope':deco['scope'], 'offset':deco['offset'], 'type':deco['type'] }
            if n.deco['type'] != n.expr.deco['type']:
                raise Exception('Incompatible types in assignment statement, line %s', n.deco['lineno'])
        case FunCall(): # no type checking is necessary
            process_expr(n, symtable)
        case While():
            process_expr(n.expr, symtable)
            if n.expr.deco['type'] != Type.BOOL:
                raise Exception('Non-boolean expression in while statement, line %s', n.deco['lineno'])
            for s in n.body:
                process_stat(s, symtable)
        case IfThenElse():
            process_expr(n.expr, symtable)
            if n.expr.deco['type'] != Type.BOOL:
                raise Exception('Non-boolean expression in if statement, line %s', n.deco['lineno'])
            for s in n.ibody + n.ebody:
                process_stat(s, symtable)
        case other: raise Exception('Unknown statement type')

def process_expr(n, symtable): # process "expression" syntax tree nodes
    match n:
        case ArithOp():
            process_expr(n.left,  symtable)
            process_expr(n.right, symtable)
            if n.left.deco['type'] != Type.INT or n.right.deco['type'] != Type.INT:
                raise Exception('Arithmetic operation over non-integer type in line %s', n.deco['lineno'])
        case LogicOp():
            process_expr(n.left,  symtable)
            process_expr(n.right, symtable)
            if (n.left.deco['type'] != n.right.deco['type']) or \
               (n.op in ['<=', '<', '>=', '>'] and n.left.deco['type'] != Type.INT) or \
               (n.op in ['&&', '||'] and n.left.deco['type'] != Type.BOOL):
                raise Exception('Boolean operation over incompatible types in line %s', n.deco['lineno'])
        case Var(): # no type checking is necessary
            deco = symtable.find_var(n.name)
            n.deco |= { 'scope':deco['scope'], 'offset':deco['offset'], 'type':deco['type'] }
        case FunCall():
            for s in n.args:
                process_expr(s, symtable)
            deco = symtable.find_fun(n.name, [a.deco['type'] for a in n.args])
            n.deco['fundeco'] = deco # save the function symbol, useful for overloading and for stack preparation
            n.deco['type']    = deco['type']
        case String(): # no type checking is necessary
            n.deco['label'] = LabelFactory.new_label() # unique label for assembly code
            symtable.ret_stack[1]['strings'].append((n.deco['label'], n.value))
        case Integer() | Boolean(): pass # no type checking is necessary
        case other: raise Exception('Unknown expression type', n)

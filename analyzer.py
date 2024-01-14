from syntree import *
from symtable import *

def build_symtable(ast):
    if not isinstance(ast, Function) or ast.name != 'main' or ast.deco['type'] != Type.VOID or len(ast.args)>0:
        raise Exception('Cannot find a valid entry point')
    symtable = SymbolTable()
    symtable.add_fun(ast.name, [], ast.deco)
    process_scope(ast, symtable)

def process_scope(fun, symtable):
    fun.deco['nonlocal'] = set() # set of nonlocal variable names in the function body, used in "readable" python transpilation only
    symtable.push_scope(fun.deco)
    for v in fun.args: # process function arguments
        symtable.add_var(*v)
    for v in fun.var:  # process local variables
        symtable.add_var(*v)
    for f in fun.fun:  # process nested functions: first add function symbols to the table
        symtable.add_fun(f.name, [d['type'] for v,d in f.args], f.deco)
    for f in fun.fun:  # then process nested function bodies
        process_scope(f, symtable)
    for s in fun.body: # process the list of statements
        process_stat(s, symtable)
    symtable.pop_scope()

def process_stat(n, symtable): # process "statement" syntax tree nodes
    if isinstance(n, Print): # no type checking is necessary
        process_expr(n.expr, symtable)
    elif isinstance(n, Return):
        if n.expr is None: return
        process_expr(n.expr, symtable)
        if symtable.ret_stack[-1]['type'] != n.expr.deco['type']:
            raise Exception('Incompatible types in return statement, line %s', n.deco['lineno'])
    elif isinstance(n, Assign):
        process_expr(n.expr, symtable)
        deco = symtable.find_var(n.name)
        n.deco['type'] = deco['type']
        if n.deco['type'] != n.expr.deco['type']:
            raise Exception('Incompatible types in assignment statement, line %s', n.deco['lineno'])
        update_nonlocals(n.name, symtable) # used in "readable" python transpilation only
    elif isinstance(n, FunCall): # no type checking is necessary
        process_expr(n, symtable)
    elif isinstance(n, While):
        process_expr(n.expr, symtable)
        if n.expr.deco['type'] != Type.BOOL:
            raise Exception('Non-boolean expression in while statement, line %s', n.deco['lineno'])
        for s in n.body:
            process_stat(s, symtable)
    elif isinstance(n, IfThenElse):
        process_expr(n.expr, symtable)
        if n.expr.deco['type'] != Type.BOOL:
            raise Exception('Non-boolean expression in if statement, line %s', n.deco['lineno'])
        for s in n.ibody + n.ebody:
            process_stat(s, symtable)
    else:
        raise Exception('Unknown statement type')

def process_expr(n, symtable): # process "expression" syntax tree nodes
    if isinstance(n, ArithOp):
        n.deco['type'] = Type.INT
        process_expr(n.left,  symtable)
        process_expr(n.right, symtable)
        if n.left.deco['type'] != Type.INT or n.right.deco['type'] != Type.INT:
            raise Exception('Arithmetic operation over non-integer type in line %s', n.deco['lineno'])
    elif isinstance(n, LogicOp):
        n.deco['type'] = Type.BOOL
        process_expr(n.left,  symtable)
        process_expr(n.right, symtable)
        if (n.left.deco['type'] != n.right.deco['type']) or \
           (n.op in ['<=', '<', '>=', '>'] and n.left.deco['type'] != Type.INT) or \
           (n.op in ['&&', '||'] and n.left.deco['type'] != Type.BOOL):
            raise Exception('Boolean operation over incompatible types in line %s', n.deco['lineno'])
    elif isinstance(n, Integer): # no type checking is necessary
        n.deco['type'] = Type.INT
    elif isinstance(n, Boolean): # no type checking is necessary
        n.deco['type'] = Type.BOOL
    elif isinstance(n, Var):     # no type checking is necessary
        deco = symtable.find_var(n.name)
        n.deco['type']   = deco['type']
        update_nonlocals(n.name, symtable) # used in "readable" python transpilation only
    elif isinstance(n, FunCall):
        for s in n.args:
            process_expr(s, symtable)
        deco = symtable.find_fun(n.name, [a.deco['type'] for a in n.args])
        n.deco['type']    = deco['type']
    elif isinstance(n, String): # no type checking is necessary
        n.deco['type']  = Type.STRING
    else:
        raise Exception('Unknown expression type', n)

def update_nonlocals(var, symtable):                    # add the variable name to the set of nonlocals
    for i in reversed(range(len(symtable.variables))):  # for all the enclosing scopes until we find the instance
        if var in symtable.variables[i]: break          # used in "readable" python transpilation only
        symtable.ret_stack[i]['nonlocal'].add(var)

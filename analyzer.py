from syntree import *
from symtable import *

def build_symtable(ast):
    if not isinstance(ast, Function) or ast.name != 'main' or ast.deco['type'] != Type.VOID or len(ast.args)>0:
        raise Exception('Cannot find a valid entry point')
    symtable = SymbolTable()
    symtable.add_fun(ast.name, [], ast.deco)
    ast.deco['strings'] = set()  # collection of constant strings from the program
    process_scope(ast, symtable)
    process_scope(ast, symtable) # ugly hack to re-propagate variable references

def process_scope(fun, symtable):
    fun.deco['nonlocal'] = set() # set of nonlocal variable names in the function body
    symtable.push_scope(fun.deco)
    for v in fun.args: # process function arguments
        symtable.add_var(*v)
    for v in fun.var:  # process local variables
        symtable.add_var(*v)
    for f in fun.fun:  # process nested functions: first add function symbols to the table
        symtable.add_fun(f.name, [t for v,t in f.args], f.deco)
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
            if n.expr is None: return # TODO semantic check for return; in non-void functions
            process_expr(n.expr, symtable)
            if symtable.ret_stack[-1]['type'] != n.expr.deco['type']:
                raise Exception('Incompatible types in return statement, line %s', n.deco['lineno'])
        case Assign():
            process_expr(n.expr, symtable)
            n.deco['type'] = symtable.find_var(n.name)
            update_nonlocals(n.name, n.deco['type'], symtable)
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
            n.deco['type'] = symtable.find_var(n.name)
            update_nonlocals(n.name, n.deco['type'], symtable)
        case FunCall():
            for s in n.args:
                process_expr(s, symtable)
            deco = symtable.find_fun(n.name, [a.deco['type'] for a in n.args])
            n.deco['fundeco'] = deco # save the function symbol, useful for overloading and for stack preparation
            n.deco['type']    = deco['type']


            if 'nonlocal' in n.deco['fundeco']:
                for v,t in n.deco['fundeco']['nonlocal']:
                    for i in reversed(range(len(symtable.variables))):     # for all the enclosing scopes until we find the instance
                        if v in symtable.variables[i]: break
                        symtable.ret_stack[i]['nonlocal'].add((v, t))


        case String(): # no type checking is necessary
            symtable.ret_stack[1]['strings'].add((n.deco['label'], n.value))
        case Integer() | Boolean(): pass # no type checking is necessary
        case other: raise Exception('Unknown expression type', n)

def update_nonlocals(name, vartype, symtable):             # add the variable name to the set of nonlocals
    for i in reversed(range(len(symtable.variables))):     # for all the enclosing scopes until we find the instance
        if name in symtable.variables[i]: break
        symtable.ret_stack[i]['nonlocal'].add((name, vartype))

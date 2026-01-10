from syntree import *
from symtable import *

def decorate(ast):
    if not isinstance(ast, Function) or ast.name != 'main' or ast.deco['type'] != Type.VOID or len(ast.args)>0:
        raise Exception('Cannot find a valid entry point')
    symtable = SymbolTable()
    symtable.add_fun(ast.name, [], ast.deco)
    ast.deco['strings'] = set()  # collection of constant strings from the program
    process_scope(ast, symtable) # N.B.: the decoration is made in two passes, this is
    process_scope(ast, symtable) # an ugly way to propagate deco['var_cnt'] from functions to funcalls
    ast.deco['scope_cnt'] = symtable.scope_cnt # total number of functions, necessary for the static scope display table allocation

def process_scope(fun, symtable):
    symtable.push_scope(fun.deco)
    for v in fun.args: # process function arguments
        symtable.add_var(v.name, v.deco)
    for v in fun.var:  # process local variables
        symtable.add_var(v.name, v.deco)
    for f in fun.fun:  # process nested functions: first add function symbols to the table
        symtable.add_fun(f.name, [v.deco['type'] for v in f.args], f.deco)
    for f in fun.fun:  # then process nested function bodies
        process_scope(f, symtable)
    for s in fun.body: # process the list of statements
        process_instruction(s, symtable)
    symtable.pop_scope()

def process_instruction(n, symtable):
    match n:
        case Print(): # no type checking is necessary
            process_instruction(n.expr, symtable)
        case Return():
            if n.expr is None: return # TODO semantic check for return; in non-void functions
            process_instruction(n.expr, symtable)
            if symtable.ret_stack[-1]['type'] != n.expr.deco['type']:
                raise Exception('Incompatible types in return statement, line %s', n.deco['lineno'])
        case Assign():
            process_instruction(n.expr, symtable)
            n.deco |= symtable.find_var(n.name)
            if n.deco['type'] != n.expr.deco['type']:
                raise Exception('Incompatible types in assignment statement, line %s', n.deco['lineno'])
        case While():
            process_instruction(n.expr, symtable)
            if n.expr.deco['type'] != Type.BOOL:
                raise Exception('Non-boolean expression in while statement, line %s', n.deco['lineno'])
            for s in n.body:
                process_instruction(s, symtable)
        case IfThenElse():
            process_instruction(n.expr, symtable)
            if n.expr.deco['type'] != Type.BOOL:
                raise Exception('Non-boolean expression in if statement, line %s', n.deco['lineno'])
            for s in n.ibody + n.ebody:
                process_instruction(s, symtable)
        case ArithOp():
            process_instruction(n.left,  symtable)
            process_instruction(n.right, symtable)
            if n.left.deco['type'] != Type.INT or n.right.deco['type'] != Type.INT:
                raise Exception('Arithmetic operation over non-integer type in line %s', n.deco['lineno'])
        case LogicOp():
            process_instruction(n.left,  symtable)
            process_instruction(n.right, symtable)
            if (n.left.deco['type'] != n.right.deco['type']) or \
               (n.op in ['<=', '<', '>=', '>'] and n.left.deco['type'] != Type.INT) or \
               (n.op in ['&&', '||'] and n.left.deco['type'] != Type.BOOL):
                raise Exception('Boolean operation over incompatible types in line %s', n.deco['lineno'])
        case Var(): # no type checking is necessary
            n.deco |= symtable.find_var(n.name)
        case FunCall():
            for s in n.args:
                process_instruction(s, symtable)
            n.deco |= symtable.find_fun(n.name, [ a.deco['type'] for a in n.args ])
        case String(): # no type checking is necessary
            symtable.ret_stack[1]['strings'].add((n.deco['label'], n.value))
        case Integer() | Boolean(): pass # no type checking is necessary
        case other: raise Exception('Unknown instruction', n)

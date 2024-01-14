from syntree import *

def transpy(n):
    funname   = n.deco['label']
    funargs   = ', '.join([v for v,t in n.args])
    nonlocals = ('nonlocal ' + ', '.join([v for v in n.deco['nonlocal'] ])) if len(n.deco['nonlocal']) else 'pass # no non-local variables'
    allocvars = ''.join(['%s = None\n' % v for v,t in n.var])
    nestedfun = ''.join([transpy(f) for f in n.fun])
    funbody   = ''.join([stat(s) for s in n.body])
    return f'def {funname}({funargs}):\n' + \
            indent(f'{nonlocals}\n'
                   f'{allocvars}\n'
                   f'{nestedfun}\n'
                   f'{funbody}\n') + \
          (f'{funname}()\n' if n.name=='main' and len(n.args)==0 else '')

def stat(n):
    if isinstance(n, Print):
        return 'print(%s, end=%s)\n' % (expr(n.expr), ["''","'\\n'"][n.newline])
    elif isinstance(n, Return):
        return 'return %s\n' % (expr(n.expr) if n.expr is not None else '')
    elif isinstance(n, Assign):
        return '%s = %s\n' % (n.name, expr(n.expr))
    elif isinstance(n, FunCall):
        return expr(n)+'\n'
    elif isinstance(n, While):
        return 'while %s:\n' % expr(n.expr) + indent([stat(s) for s in n.body] or 'pass')
    elif isinstance(n, IfThenElse):
        return 'if %s:\n%selse:\n%s\n' % (expr(n.expr),
                                        indent([stat(s) for s in n.ibody] or 'pass'),
                                        indent([stat(s) for s in n.ebody] or 'pass'))
    raise Exception('Unknown statement type', n)

def expr(n):
    if isinstance(n, ArithOp) or isinstance(n, LogicOp):
        pyeq = {'/':'//', '||':'or', '&&':'and'}
        pyop = pyeq[n.op] if n.op in pyeq else n.op
        return '(%s) %s (%s)' % (expr(n.left), pyop, expr(n.right))
    elif isinstance(n, Integer) or isinstance(n, Boolean):
        return str(n.value)
    elif isinstance(n, String):
        return '"' + n.value + '"'
    elif isinstance(n, Var):
        return n.name
    elif isinstance(n, FunCall):
        return '%s(%s)' % (n.deco['fundeco']['label'], ', '.join([expr(s) for s in n.args]))
    raise Exception('Unknown expression type', n)

def indent(array):
    multiline = ''.join([str(entry) for entry in array])
    if multiline == '': return ''
    return '\t'+'\n\t'.join(multiline.splitlines()) + '\n'

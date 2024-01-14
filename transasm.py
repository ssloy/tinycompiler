from syntree import *
from analyzer import LabelFactory
from transasm_recipe import templates

def transasm(n):
    strings = ''.join([templates['ascii'].format(**locals()) for label,string in n.deco['strings']])
    display_size = n.deco['scope_cnt']*4
    offset       = n.deco['scope']*4
    main         = n.deco['label']
    varsize      = len(n.var)*4
    functions    = fun(n)
    return templates['program'].format(**locals())

def fun(n):
    label  = n.deco['label']
    nested = ''.join([ fun(f) for f in n.fun ])
    body   = ''.join([stat(s) for s in n.body])
    return f'{label}:\n{body}\n\tret\n{nested}\n'

def stat(n):
    if isinstance(n, Print):
        newline = templates['print_linebreak'] if n.newline else ''
        if n.expr.deco['type']==Type.INT:
            return templates['print_int'].format(expr = expr(n.expr), newline = newline)
        elif n.expr.deco['type']==Type.BOOL:
            return templates['print_bool'].format(expr = expr(n.expr), newline = newline)
        elif n.expr.deco['type']==Type.STRING:
            return templates['print_string'].format(label = n.expr.deco['label'], newline = newline)
        else:
            raise Exception('Unknown expression type', n.expr)
    elif isinstance(n, Return):
        return (expr(n.expr) if n.expr is not None and n.expr.deco['type'] != Type.VOID else '') + '\tret\n'
    elif isinstance(n, Assign):
        return templates['assign'].format(expression = expr(n.expr),
                                               scope = n.deco['scope']*4,
                                            variable = n.deco['offset']*4)
    elif isinstance(n, FunCall):
        return expr(n)
    elif isinstance(n, While):
        return templates['while'].format(condition = expr(n.expr),
                                            label1 = LabelFactory.new_label(),
                                            label2 = LabelFactory.new_label(),
                                              body = ''.join([stat(s) for s in n.body]))
    elif isinstance(n, IfThenElse):
        return templates['ifthenelse'].format(condition = expr(n.expr),
                                                 label1 = LabelFactory.new_label(),
                                                 label2 = LabelFactory.new_label(),
                                                  ibody = ''.join([stat(s) for s in n.ibody]),
                                                  ebody = ''.join([stat(s) for s in n.ebody]))
    raise Exception('Unknown statement type', n)

def expr(n): # convention: all expressions save their results to eax
    if isinstance(n, ArithOp) or isinstance(n, LogicOp):
        args = expr(n.left) + '\tpushl %eax\n' + expr(n.right) + '\tmovl %eax, %ebx\n\tpopl %eax\n'
        pyeq1 = {'+':'addl', '-':'subl', '*':'imull', '||':'orl', '&&':'andl'}
        pyeq2 = {'<=':'jle', '<':'jl', '>=':'jge', '>':'jg', '==':'je', '!=':'jne'}
        if n.op in pyeq1:
            return args + f'\t{pyeq1[n.op]} %ebx, %eax\n'
        elif n.op in pyeq2:
            return args + f'\tcmp %ebx, %eax\n\tmovl $1, %eax\n\t{pyeq2[n.op]} 1f\n\txorl %eax, %eax\n1:\n'
        elif n.op=='/':
            return args + '\tcdq\n\tidivl %ebx, %eax\n'
        elif n.op=='%':
            return args + '\tcdq\n\tidivl %ebx, %eax\n\tmovl %edx, %eax\n'
        raise Exception('Unknown binary operation')
    elif isinstance(n, Integer) or isinstance(n, Boolean):
        return f'\tmovl ${int(n.value)}, %eax\n'
    elif isinstance(n, Var):
        return templates['var'].format(scope = n.deco['scope']*4, variable = n.deco['offset']*4)
    elif isinstance(n, FunCall):
        return templates['funcall'].format(allocargs = ''.join(['%s\tpushl %%eax\n' % expr(a) for a in n.args]),
                                             varsize = len(n.deco['fundeco']['local'])*4,
                                            disphead = len(n.deco['fundeco']['local'])*4 + len(n.args)*4 - 4,
                                               scope = n.deco['fundeco']['scope']*4,
                                            funlabel = n.deco['fundeco']['label'])
    raise Exception('Unknown expression type', n)

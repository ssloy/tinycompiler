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
    match n:
        case Print():
            match n.expr.deco['type']:
                case Type.INT:
                    asm = templates['print_int'].format(expr = expr(n.expr))
                case Type.BOOL:
                    asm = templates['print_bool'].format(expr = expr(n.expr))
                case Type.STRING:
                    asm = templates['print_string'].format(label = n.expr.deco['label'])
                case other: raise Exception('Unknown expression type', n.expr)
            return asm + (templates['print_linebreak'] if n.newline else '')
        case Return():
            return (expr(n.expr) if n.expr is not None and n.expr.deco['type'] != Type.VOID else '') + '\tret\n'
        case Assign():
            return templates['assign'].format(expression = expr(n.expr),
                                                   scope = n.deco['scope']*4,
                                                variable = n.deco['offset']*4)
        case FunCall(): return expr(n)
        case While():
            return templates['while'].format(condition = expr(n.expr),
                                                label1 = LabelFactory.new_label(),
                                                label2 = LabelFactory.new_label(),
                                                  body = ''.join([stat(s) for s in n.body]))
        case IfThenElse():
            return templates['ifthenelse'].format(condition = expr(n.expr),
                                                     label1 = LabelFactory.new_label(),
                                                     label2 = LabelFactory.new_label(),
                                                      ibody = ''.join([stat(s) for s in n.ibody]),
                                                      ebody = ''.join([stat(s) for s in n.ebody]))
        case other: raise Exception('Unknown statement type', n)

def expr(n): # convention: all expressions save their results to eax
    match n:
        case ArithOp() | LogicOp():
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
        case Integer() | Boolean():
            return f'\tmovl ${int(n.value)}, %eax\n'
        case Var():
            return templates['var'].format(scope = n.deco['scope']*4, variable = n.deco['offset']*4)
        case FunCall():
            return templates['funcall'].format(allocargs = ''.join(['%s\tpushl %%eax\n' % expr(a) for a in n.args]),
                                                 varsize = n.deco['var_cnt']*4,
                                                disphead = n.deco['var_cnt']*4 + len(n.args)*4 - 4,
                                                   scope = n.deco['scope']*4,
                                                funlabel = n.deco['label'])
        case other: raise Exception('Unknown expression type', n)

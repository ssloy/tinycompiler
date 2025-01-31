from syntree import *
from analyzer import LabelFactory
from transllvm_recipe import templates

def transllvm(n):
    strings = ''.join([templates['ascii'].format(label=label, size=len(string)+1, string=string) for label,string in n.deco['strings']]) # TODO \n => \0A etc
    main         = n.deco['label']
    functions    = fun(n)
    return templates['program'].format(**locals())

def fun(n):
    label  = n.deco['label']
    nested = ''.join([ fun(f) for f in n.fun ])
    rettype = ["void", "i32", "i1"][n.deco['type']]
    retval = "ret void" if n.deco['type']==Type.VOID else ""
    body   = ''.join([stat(s) for s in n.body])
    return templates['function'].format(**locals())

def stat(n):
    match n:
        case Print():
            match n.expr.deco['type']:
                case Type.INT:
                    asm = templates['print_int'].format(expr = expr(n.expr), label = LabelFactory.cur_label())
                case Type.BOOL:
                    asm = templates['print_bool'].format(expr = expr(n.expr), label = LabelFactory.cur_label())
                case Type.STRING:
                    asm = templates['print_string'].format(label = n.expr.deco['label'])
                case other: raise Exception('Unknown expression type', n.expr)
            return asm + (templates['print_linebreak'] if n.newline else '')
        case other: raise Exception('Unknown statement type', n)



def expr(n): # convention: all expressions save their results to eax
    match n:
        case ArithOp() | LogicOp():
            e1, l1 = expr(n.left),  LabelFactory.cur_label()
            e2, l2 = expr(n.right), LabelFactory.cur_label()
            t = "i32" if n.left.deco['type']==Type.INT else "i1"
            op = {'+':'add', '-':'sub', '*':'mul', '/':'sdiv', '%':'srem','||':'or', '&&':'and','<=':'icmp sle', '<':'icmp slt', '>=':'icmp sge', '>':'icmp sgt', '==':'icmp eq', '!=':'icmp ne'}
            l = LabelFactory.new_label()
            return f'\t{e1}\n\t{e2}\n\t%{l} = {op[n.op]} {t} %{l1}, %{l2}\n';
        case Integer():
            label = LabelFactory.new_label()
            return f'\t%{label} = add i32 0, {n.value}\n'
        case Boolean():
            label = LabelFactory.new_label()
            return f'\t%{label} = or i1 0, {int(n.value)}\n'
        case other: raise Exception('Unknown expression type', n)

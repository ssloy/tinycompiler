from syntree import *
from analyzer import LabelFactory
from transllvm_recipe import templates

def transllvm(n):
    strings = ''.join([templates['ascii'].format(label=label, size=len(string)+1, string=string) for label,string in n.deco['strings']]) # TODO \n => \0A etc
    main         = n.deco['label']
    functions    = fun(n)
    return templates['program'].format(**locals())

def lltype(t):
    return ['void', 'i32', 'i1'][t]

def fun(n):
    label  = n.deco['label']
    alloca = ''.join([templates['alloca'].format(name=v[0], vartype=lltype(v[1]['type'])) for v in n.var])
    nested = ''.join([ fun(f) for f in n.fun ])
    rettype = lltype(n.deco['type'])
    retval = 'ret void' if n.deco['type']==Type.VOID else ''
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
            return asm + (templates['print_newline'] if n.newline else '')
        case Assign():
            return templates['assign'].format(expr    = expr(n.expr),
                                              label   = LabelFactory.cur_label(),
                                              vartype = lltype(n.deco['type']),
                                              varname = n.name)
        case While():
            return templates['while'].format(expr   = expr(n.expr),
                                             label1 = LabelFactory.cur_label(),
                                             label2 = LabelFactory.new_label(),
                                             body   = ''.join([stat(s) for s in n.body]))
        case IfThenElse():
            return templates['ifthenelse'].format(expr   = expr(n.expr),
                                                  label1 = LabelFactory.cur_label(),
                                                  label2 = LabelFactory.new_label(),
                                                  ibody  = ''.join([stat(s) for s in n.ibody]),
                                                  ebody  = ''.join([stat(s) for s in n.ebody]))
        case other: raise Exception('Unknown statement type', n)



def expr(n): # convention: all expressions save their results to eax
    match n:
        case ArithOp() | LogicOp():
            e1, l1 = expr(n.left),  LabelFactory.cur_label()
            e2, l2 = expr(n.right), LabelFactory.cur_label()
            t = lltype(n.left.deco['type'])
            op = {'+':'add', '-':'sub', '*':'mul', '/':'sdiv', '%':'srem','||':'or', '&&':'and','<=':'icmp sle', '<':'icmp slt', '>=':'icmp sge', '>':'icmp sgt', '==':'icmp eq', '!=':'icmp ne'}
            l = LabelFactory.new_label()
            return f'{e1}{e2}\t%{l} = {op[n.op]} {t} %{l1}, %{l2}\n';
        case Var():
            label = LabelFactory.new_label()
            vartype = 'i1' if n.deco['type']==Type.BOOL else 'i32'
            return f'\t%{label} = load {vartype}, ptr %{n.name}\n'
        case Integer():
            label = LabelFactory.new_label()
            return f'\t%{label} = add i32 0, {n.value}\n'
        case Boolean():
            label = LabelFactory.new_label()
            return f'\t%{label} = or i1 0, {int(n.value)}\n'
        case other: raise Exception('Unknown expression type', n)

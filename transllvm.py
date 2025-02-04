from syntree import *
from transllvm_recipe import templates

def transllvm(n):
    strings = ''.join([templates['ascii'].format( label  = label,
                                                  size   = len(string)+1,                               # +1 for null termination
                                                  string = ''.join(['\\%02x' % ord(x) for x in string]) # hex escape the string
                                                 ) for label,string in n.deco['strings']])
    main         = n.deco['label']
    functions    = fun(n)
    return templates['program'].format(**locals())

def lltype(t):
    return ['void', 'i32', 'i1'][t]

def fun(n):
    label   = n.deco['label']
    args    = ', '.join([ '{t}* %{n}'   .format(n = a[0], t = lltype(a[1])) for a in n.deco['nonlocal'] ] +
                        [ '{t} %{n}.arg'.format(n = a.deco['fullname'], t = lltype(a.deco['type'])) for a in n.args ])
    alloca1 = ''.join([templates['alloca1'].format(name=v.deco['fullname'], vartype=lltype(v.deco['type'])) for v in n.args])
    alloca2 = ''.join([templates['alloca2'].format(name=v.deco['fullname'], vartype=lltype(v.deco['type'])) for v in n.var])
    nested  = ''.join([ fun(f) for f in n.fun ])
    rettype = lltype(n.deco['type'])
    retval  = '\tret void' if n.deco['type']==Type.VOID else '\tunreachable'
    body    = ''.join([stat(s) for s in n.body])
    return templates['function'].format(**locals())

def stat(n):
    match n:
        case Print():
            match n.expr.deco['type']:
                case Type.INT:
                    asm = templates['print_int'].format(expr = stat(n.expr), label = LabelFactory.cur_label())
                case Type.BOOL:
                    asm = templates['print_bool'].format(expr = stat(n.expr), label = LabelFactory.cur_label())
                case Type.STRING:
                    asm = templates['print_string'].format(label = n.expr.deco['label'])
                case other: raise Exception('Unknown expression type', n.expr)
            return asm + (templates['print_newline'] if n.newline else '')
        case Return():
            return templates['return'].format(expr    = stat(n.expr) if n.expr else '',
                                              rettype = lltype(n.expr.deco['type']) if n.expr else 'void',
                                              label   = LabelFactory.cur_label() if n.expr else '')
        case Assign():
            return templates['assign'].format(expr    = stat(n.expr),
                                              label   = LabelFactory.cur_label(),
                                              vartype = lltype(n.deco['type']),
                                              varname = n.deco['fullname'])
        case While():
            return templates['while'].format(expr   = stat(n.expr),
                                             label1 = LabelFactory.cur_label(),
                                             label2 = LabelFactory.new_label(),
                                             body   = ''.join([stat(s) for s in n.body]))
        case IfThenElse():
            return templates['ifthenelse'].format(expr   = stat(n.expr),
                                                  label1 = LabelFactory.cur_label(),
                                                  label2 = LabelFactory.new_label(),
                                                  ibody  = ''.join([stat(s) for s in n.ibody]),
                                                  ebody  = ''.join([stat(s) for s in n.ebody]))
        case ArithOp() | LogicOp():
            e1, l1 = stat(n.left),  LabelFactory.cur_label()
            e2, l2 = stat(n.right), LabelFactory.cur_label()
            t = lltype(n.left.deco['type'])
            op = {'+':'add', '-':'sub', '*':'mul', '/':'sdiv', '%':'srem','||':'or', '&&':'and','<=':'icmp sle', '<':'icmp slt', '>=':'icmp sge', '>':'icmp sgt', '==':'icmp eq', '!=':'icmp ne'}
            l = LabelFactory.new_label()
            return f'{e1}{e2}\t%{l} = {op[n.op]} {t} %{l1}, %{l2}\n';
        case Integer():
            label = LabelFactory.new_label()
            return f'\t%{label} = add i32 0, {n.value}\n'
        case Boolean():
            label = LabelFactory.new_label()
            return f'\t%{label} = or i1 0, {int(n.value)}\n'
        case Var():
            label = LabelFactory.new_label()
            vartype = 'i1' if n.deco['type']==Type.BOOL else 'i32'
            return f'\t%{label} = load {vartype}, {vartype}* %{n.deco["fullname"]}\n'
        case FunCall():
            arg_bodies = ''
            args = []
            for e in n.args:
                arg_bodies += stat(e)
                args.append(lltype(e.deco['type']) + ' %' + LabelFactory.cur_label())
            args = ', '.join([ '{t}* %{n}'.format(n = a[0], t = lltype(a[1])) for a in n.deco['nonlocal'] ] + args)
            rettype = lltype(n.deco['type'])
            label1 = n.deco['label']
            lvalue = '' if rettype=='void' else '%' + LabelFactory.new_label() + ' = '
            return f'{arg_bodies}\t{lvalue}call {rettype} @{label1}({args})\n'
        case other: raise Exception('Unknown instruction', n)

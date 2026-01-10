class LabelFactory: # this is a suffix to add to all function names
    counter = 0     # in particular, it is useful for function overloading
    @staticmethod   # it is also useful for different goto labels (loops, conditional statements etc) in assembly code
    def cur_label():
        return "uniqstr%d" % LabelFactory.counter
    def new_label():
        LabelFactory.counter += 1
        return "uniqstr%d" % LabelFactory.counter

class Type:
    VOID   = 0
    INT    = 1
    BOOL   = 2
    STRING = 3

class Function:
    def __init__(self, name, args, var, fun, body, deco):
        self.name = name                                                 # function name, string
        self.args = args                                                 # function arguments, list of tuples (name, type)
        self.var  = var                                                  # local variables, list of Var objects
        self.fun  = fun                                                  # nested functions, list of Function nodes
        self.body = body                                                 # function body, list of statement nodes (Print/Return/Assign/While/IfThenElse/FunCall)
        self.deco = deco | {'label' : name+'_'+LabelFactory.new_label()} # decoration dictionary to be filled by the parser (line number) and by the semantic analyzer (return type, scope id etc)

class Print:
    def __init__(self, expr, newline, deco):
        self.expr, self.newline, self.deco = expr, newline, deco

class Return:
    def __init__(self, expr, deco):
        self.expr, self.deco = expr, deco

class Assign:
    def __init__(self, name, expr, deco):
        self.name, self.expr, self.deco = name, expr, deco

class While:
    def __init__(self, expr, body, deco):
        self.expr, self.body, self.deco = expr, body, deco

class IfThenElse:
    def __init__(self, expr, ibody, ebody, deco):
        self.expr, self.ibody, self.ebody, self.deco = expr, ibody, ebody, deco

class ArithOp:
    def __init__(self, op, left, right, deco):
        self.op, self.left, self.right, self.deco = op, left, right, deco | {'type' : Type.INT}

class LogicOp:
    def __init__(self, op, left, right, deco):
        self.op, self.left, self.right, self.deco = op, left, right, deco | {'type' : Type.BOOL}

class Integer:
    def __init__(self, value, deco):
        self.value, self.deco = value, deco | {'type' : Type.INT}

class Boolean:
    def __init__(self, value, deco):
        self.value, self.deco = value, deco | {'type' : Type.BOOL}

class String:
    def __init__(self, value, deco):
        self.value, self.deco = value, deco | {'type' : Type.STRING, 'label' : LabelFactory.new_label() }

class Var:
    def __init__(self, name, deco):
        self.name, self.deco = name, deco

class FunCall: # depending on the context, a function call can be a statement or an expression
    def __init__(self, name, args, deco):
        self.name, self.args, self.deco = name, args, deco

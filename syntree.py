class Type:
    VOID   = 0
    INT    = 1
    BOOL   = 2
    STRING = 3

class Function:
    def __init__(self, name, args, var, fun, body, deco=None):
        self.name = name       # function name, string
        self.args = args       # function arguments, list of tuples (name, type)
        self.var  = var        # local variables, list of tuples (name, type)
        self.fun  = fun        # nested functions, list of Function nodes
        self.body = body       # function body, list of statement nodes (Print/Return/Assign/While/IfThenElse/FunCall)
        self.deco = deco or {} # decoration dictionary to be filled by the parser (line number) and by the semantic analyzer (return type, scope id etc)

# statements
class Print:
    def __init__(self, expr, newline, deco=None):
        self.expr, self.newline, self.deco = expr, newline, deco or {}

class Return:
    def __init__(self, expr, deco=None):
        self.expr, self.deco = expr, deco or {}

class Assign:
    def __init__(self, name, expr, deco=None):
        self.name, self.expr, self.deco = name, expr, deco or {}

class While:
    def __init__(self, expr, body, deco=None):
        self.expr, self.body, self.deco = expr, body, deco or {}

class IfThenElse:
    def __init__(self, expr, ibody, ebody, deco=None):
        self.expr, self.ibody, self.ebody, self.deco = expr, ibody, ebody, deco or {}

# expressions
class ArithOp:
    def __init__(self, op, left, right, deco=None):
        self.op, self.left, self.right, self.deco = op, left, right, (deco or {}) | {'type':Type.INT}

class LogicOp:
    def __init__(self, op, left, right, deco=None):
        self.op, self.left, self.right, self.deco = op, left, right, (deco or {}) | {'type':Type.BOOL}

class Integer:
    def __init__(self, value, deco=None):
        self.value, self.deco = value, (deco or {}) | {'type':Type.INT}

class Boolean:
    def __init__(self, value, deco=None):
        self.value, self.deco = value, (deco or {}) | {'type':Type.BOOL}

class String:
    def __init__(self, value, deco=None):
        self.value, self.deco = value, (deco or {}) | {'type':Type.STRING}

class Var:
    def __init__(self, name, deco=None):
        self.name, self.deco = name, deco or {}

class FunCall: # depending on the context, a function call can be a statement or an expression
    def __init__(self, name, args, deco=None):
        self.name, self.args, self.deco = name, args, deco or {}

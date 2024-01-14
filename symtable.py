class SymbolTable():
    def __init__(self):
        self.variables = [{}]     # stack of variable symbol tables
        self.functions = [{}]     # stack of function symbol tables
        self.ret_stack = [ None ] # stack of enclosing function symbols, useful for return statements
    def add_fun(self, name, argtypes, deco):  # a function can be identified by its name and a list of argument types, e.g.
        signature = (name, *argtypes)         # fun foo(x:bool, y:int) : int {...} has ('foo',Type.BOOL,Type.INT) signature
        if signature in self.functions[-1]:
            raise Exception('Double declaration of the function %s %s' % (signature[0], signature[1:]))
        self.functions[-1][signature] = deco

    def add_var(self, name, deco):
        if name in self.variables[-1]:
            raise Exception('Double declaration of the variable %s' % name)
        self.variables[-1][name] = deco

    def push_scope(self, deco):
        self.variables.append({})
        self.functions.append({})
        self.ret_stack.append(deco)

    def pop_scope(self):
        self.variables.pop()
        self.functions.pop()
        self.ret_stack.pop()

    def find_var(self, name):
        for i in reversed(range(len(self.variables))):
            if name in self.variables[i]:
                return self.variables[i][name]
        raise Exception('No declaration for the variable %s' % name)

    def find_fun(self, name, argtypes):
        signature = (name, *argtypes)
        for i in reversed(range(len(self.functions))):
            if signature in self.functions[i]:
                return self.functions[i][signature]
        raise Exception('No declaration for the function %s' % signature[0], signature[1:])

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
        deco['fullname'] = self.ret_stack[-1]['label'] + '.' + name

    def push_scope(self, deco):
        deco['nonlocal'] = set() # set of nonlocal variable names in the function body
        self.variables.append({})
        self.functions.append({})
        self.ret_stack.append(deco)

    def pop_scope(self):
        self.variables.pop()
        self.functions.pop()
        self.ret_stack.pop()

    def find_var(self, name):
        try:
            for i in reversed(range(len(self.variables))): # find the variable symbol
                if name in self.variables[i]: break
            deco = self.variables[i][name]
            for i in range(i+1, len(self.variables)):      # propagate the pointer to the current context
                self.ret_stack[i]['nonlocal'].add((deco['fullname'], deco['type']))
            return deco
        except KeyError: raise Exception('No declaration for the variable %s' % name)

    def find_fun(self, name, argtypes):
        try:
            signature = (name, *argtypes)
            for i in reversed(range(len(self.functions))): # find the function symbol
                if signature in self.functions[i]: break
            deco = self.functions[i][signature]
            if 'nonlocal' in deco:                         # propagate context pointers to the function call
                for fullname,t in deco['nonlocal']:
                    label = fullname.partition('.')[0]
                    for f in reversed(self.ret_stack):
                        if f['label'] == label: break
                        f['nonlocal'].add((fullname, t))
            return deco
        except KeyError: raise Exception('No declaration for the function %s' % signature[0], signature[1:])

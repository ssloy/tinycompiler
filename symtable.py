class SymbolTable():
    def __init__(self):
        self.variables = [{}]     # stack of variable symbol tables
        self.ret_stack = [ None ] # stack of enclosing function symbols, useful for return statements

    def add_var(self, name, deco):
        if name in self.variables[-1]:
            raise Exception('Double declaration of the variable %s' % name)
        self.variables[-1][name] = deco

    def push_scope(self, deco):
        self.variables.append({})
        self.ret_stack.append(deco)

    def pop_scope(self):
        self.variables.pop()
        self.ret_stack.pop()

    def find_var(self, name):
        for i in reversed(range(len(self.variables))):
            if name in self.variables[i]:
                return self.variables[i][name]
        raise Exception('No declaration for the variable %s' % name)

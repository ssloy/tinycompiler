###################
# IR instructions #
###################

class Branch:
    def __init__(self, cond, ilabel, elabel):
        self.cond, self.ilabel, self.elabel = cond, ilabel, elabel

    def __repr__(self):
        return f'br i1 {self.cond}, label {self.ilabel}, label {self.elabel}'

class Jump:
    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return f'br label {self.label}'

class Load:
    def __init__(self, reg, ptr):
        self.reg, self.ptr = reg, ptr

    def __repr__(self):
        return f'{self.reg} = load {self.ptr}'

class Store:
    def __init__(self, value, ptr):
        self.value, self.ptr = value, ptr

    def __repr__(self):
        return f'store {self.value}, {self.ptr}'

class Alloca:
    def __init__(self, ptr):
        self.ptr = ptr

    def __repr__(self):
        return f'{self.ptr} = alloca'

class Phi:
    def __init__(self, reg, choice=None):
        self.reg, self.choice = reg, choice or {}

    def __repr__(self):
        choice = ', '.join([ f'[{value}, {block}]' for block, value in self.choice.items() ])
        return f'{self.reg} = phi {choice}'

######################
# Control flow graph #
######################

class BasicBlock:
    def __init__(self, label):
        self.label = label
        self.instructions  = []
        self.phi_functions = {} # map variable -> { Phi object }
        self.successors    = [] # do we need successors? branch/jump instructions may suffice
        self.predecessors  = []

    def add_successor(self, block):
        if block not in self.successors:
            self.successors.append(block)
            block.predecessors.append(self)

    def add_phi_function(self, reg):
        self.phi_functions[reg] = Phi(reg + '_' + self.label)

    def __repr__(self):
        return f'{self.label}'

class ControlFlowGraph:
    def __init__(self):
        self.blocks = {}
        self.df = {}

    def add_block(self, label):
        self.blocks[label] = BasicBlock(label)

    def add_edge(self, from_label, to_label):
        from_block = self.blocks[from_label]
        to_block   = self.blocks[to_label]
        from_block.add_successor(to_block)

    def __repr__(self):
        result = 'Control Flow Graph:\n'
        for block in self.blocks.values():
            result += f'{block.label}:\n'
            result += '  Phi: ' + ', '.join([ str(phi) for phi in block.phi_functions.values() ]) + '\n'
            result += '  Instr: ' + '\n          '.join([ str(i) for i in block.instructions ] ) + '\n'
            result += f'  Successors: {[b.label for b in block.successors]}\n'
            result += f'  Predecessors: {[b.label for b in block.predecessors]}\n\n'
        return result

    def compute_dominance_frontier(self):
        def dfs(block, visited, postorder):
            visited.add(block)
            for b in block.successors:
                if b not in visited: dfs(b, visited, postorder)
            postorder.append(block)
        postorder = []                                              # for efficiency reasons, we visit blocks in a way that ensures
        dfs(self.blocks['source'], set(), postorder)                # processing of each block after its predecessors have been processed

        dom = { b : set(self.blocks.values()) for b in self.blocks.values() }
        dom[ self.blocks['source'] ] = { self.blocks['source'] }    # dom[b] contains every block that dominates b
        changed = True
        while changed:                                              # the iterative dominator algorithm [Cooper, Harvey and Kennedy, 2006]
            changed = False
            for b in postorder[-2::-1]:                             # for all blocks (except the source) in reverse postorder
                new_dom = set.intersection(*[ dom[p] for p in b.predecessors ]) | { b }
                if dom[b] != new_dom:
                    dom[b] = new_dom
                    changed = True

        idom = { self.blocks['source'] : None }                     # idom[b] contains exactly one block, the immediate dominator of b
        for b in postorder[-2::-1]:                                 # reverse or not we do not care here, but do not visit the source block
            idom[b] = max(dom[b] - {b}, key=lambda x: len(dom[x]))  # immediate dominator is the one with the maximum number of dominators (except the block itself)

        self.df = { b : set() for b in self.blocks.values() }
        for b in self.blocks.values():                              # the dominance-frontier algorithm
            if len(b.predecessors) < 2: continue
            for p in b.predecessors:
                runner = p
                while runner != idom[b]:
                    self.df[runner].add(b)
                    runner = idom[runner]

    def mem2reg(self):
        self.compute_dominance_frontier()

        variables = [ i.ptr for i in self.blocks['source'].instructions if isinstance(i, Alloca) ]
        phi = { v:set() for v in variables }                        # map (variable -> set of basic blocks)
        for v in variables:
            blocks_with_store = { b for b in self.blocks.values() for i in b.instructions if isinstance(i, Store) and i.ptr==v }
            blocks_to_consider = blocks_with_store.copy()
            while blocks_to_consider:
                block = blocks_to_consider.pop()
                for frontier in self.df[block]:
                    phi[v].add(frontier)
                    if frontier not in blocks_with_store:
                        blocks_to_consider.add(frontier)
        print(phi)
        for v, bb in phi.items():
            for b in bb:
                b.add_phi_function(v)

        def store_load(block, visited, stack):
            def find_variable(v, stack):
                for frame in reversed(stack):
                    if v in frame: return frame[v]

            for v, phi in block.phi_functions.items():
                b,val = find_variable(v, stack)
                phi.choice[b] = val


            if block in visited: return

            visited.add(block)

            for i in block.instructions[:]: # iterate through a copy since we modify the list
                match i:
                    case Load():
                        pass
#                let (_, load_value) = decide_variable_value(from_variable, current_variable_value);
#                block.remove(statement);
#                function.replace(to, load_value);
# from now on, all occurencies of self.reg are to be replaced by stack[-1][i.ptr][
                    case Store():
#                        print(i)
                        stack[-1][i.ptr] = (block.label, i.value)
                        block.instructions.remove(i)
                    case Branch():
                        stack.append({})
                        store_load(self.blocks[i.ilabel], visited, stack)
                        stack.pop()
                        stack.append({})
                        store_load(self.blocks[i.elabel], visited, stack)
                        stack.pop()
                    case Jump():
                        store_load(self.blocks[i.label],  visited, stack)

        stack = [{}] # stack of maps (variable -> (block, value))
        store_load(self.blocks['source'], set(), stack)


cfg = ControlFlowGraph()
cfg.add_block('source')
cfg.add_block('bb1')
cfg.add_block('bb2')
cfg.add_block('bb3')
cfg.add_block('bb4')
cfg.add_block('bb5')
cfg.add_block('bb6')
cfg.add_block('bb7')
cfg.add_block('bb8')
cfg.add_block('sink')

cfg.blocks['source'].instructions.append(Alloca('%a'))
cfg.blocks['source'].instructions.append(Jump('bb1'))
cfg.add_edge('source', 'bb1')

cfg.blocks['bb1'].instructions.append(Store(1, '%a'))
cfg.blocks['bb1'].instructions.append(Branch('foo', 'bb2', 'bb4'))
cfg.add_edge('bb1', 'bb2')
cfg.add_edge('bb1', 'bb4')

cfg.blocks['bb2'].instructions.append(Load('%a0', '%a'))
cfg.blocks['bb2'].instructions.append('%t0 = add %a0, 1')
cfg.blocks['bb2'].instructions.append(Store('%t0', '%a'))
cfg.blocks['bb2'].instructions.append(Jump('bb3'))
cfg.add_edge('bb2', 'bb3')

cfg.blocks['bb3'].instructions.append(Load('%a1', '%a'))
cfg.blocks['bb3'].instructions.append('%t1 = add %a1, %a1')
cfg.blocks['bb3'].instructions.append(Store('%t1', '%a'))
cfg.blocks['bb3'].instructions.append(Branch('foo', 'bb8', 'bb2'))
cfg.add_edge('bb3', 'bb2')
cfg.add_edge('bb3', 'bb8')

cfg.blocks['bb5'].instructions.append(Load('%a2', '%a'))
cfg.blocks['bb5'].instructions.append(Store(2, '%a'))
cfg.blocks['bb5'].instructions.append(Jump('bb7'))
cfg.add_edge('bb5', 'bb7')

cfg.blocks['bb4'].instructions.append(Branch('foo', 'bb5', 'bb6'))
cfg.add_edge('bb4', 'bb5')
cfg.add_edge('bb4', 'bb6')

cfg.blocks['bb6'].instructions.append(Load('%a3', '%a'))
cfg.blocks['bb6'].instructions.append(Store(3, '%a'))
cfg.blocks['bb6'].instructions.append(Jump('bb7'))
cfg.add_edge('bb6', 'bb7')

cfg.blocks['bb7'].instructions.append(Load('%a4', '%a'))
cfg.blocks['bb7'].instructions.append(Jump('bb8'))
cfg.add_edge('bb7', 'bb8')

cfg.blocks['bb8'].instructions.append(Load('%a5', '%a'))
cfg.blocks['bb8'].instructions.append('ret %a5')
cfg.add_edge('bb8', 'sink')
print(cfg)

cfg.mem2reg()

print(cfg)




class Instruction:
    def __init__(self, str, t=None, a=None, b=None, c=None):
        self.str, self.t, self.a, self.b, self.c = str, t, a, b, c

    def __repr__(self):
        return self.str.format(a=self.a, b=self.b, c=self.c, t=self.t)

class Phi:
    def __init__(self, reg, choice=None):
        self.reg, self.choice = reg, choice or {}

    def __repr__(self):
        choice = ', '.join([ f'[{value}, {block}]' for block, value in self.choice.items() ])
        return f'{self.reg} = phi {choice}'

class BasicBlock:
    def __init__(self, label):
        self.label = label
        self.instructions  = []
        self.phi_functions = {} # map variable -> { Phi object }
        self.successors    = set() # do we need successors? branch/jump instr may suffice
        self.predecessors  = set() # no need for those, can compute on the fly
        self.replacements  = {} # TODO: incorporate replacements into individual instr

    def add_successor(self, block):
        if block not in self.successors:
            self.successors.add(block)
            block.predecessors.add(self)

    def add_phi_function(self, reg):
        self.phi_functions[reg] = Phi(reg + '_' + self.label)

    def replace(self):
        for i in self.instructions:
            i.a, i.b, i.c = ( self.replacements.get(s, s) for s in (i.a, i.b, i.c) )
        self.replacements = {}

    def __repr__(self):
        self.replace()
        return f'{self.label}:\n' + \
                ''.join( [ f'{phi}\n' for phi in self.phi_functions.values() ] ) + \
                ''.join( [ f'{i}\n' for i in self.instructions ] )

class ControlFlowGraph:
    def __init__(self):
        self.blocks = {}
        self.df = {}

    def add_block(self, label):
        self.blocks[label] = BasicBlock(label)

    def compute_adjacency(self):
        for b in self.blocks.values():
            i = b.instructions[-1]
            for succ in [i.a] if 'br label' in i.str else [i.b, i.c]:
                if succ:
                    self.add_edge(b.label, succ)

    def add_edge(self, from_label, to_label):
        from_block = self.blocks[from_label]
        to_block   = self.blocks[to_label]
        from_block.add_successor(to_block)

    def __repr__(self):
        result = 'Control Flow Graph:\n'
        for block in self.blocks.values():
            result += f'{block}\n'
        return result

    def compute_dominance_frontier(self):
        def dfs(block, visited, postorder):
            visited.add(block)
            for b in block.successors:
                if b not in visited: dfs(b, visited, postorder)
            postorder.append(block)
        postorder = []                                              # for efficiency reasons, we visit blocks in a way that ensures
        dfs(self.blocks['entry'], set(), postorder)                 # processing of each block after its predecessors have been processed

        dom = { b : set(self.blocks.values()) for b in self.blocks.values() }
        dom[ self.blocks['entry'] ] = { self.blocks['entry'] }      # dom[b] contains every block that dominates b
        changed = True
        while changed:                                              # the iterative dominator algorithm [Cooper, Harvey and Kennedy, 2006]
            changed = False
            for b in postorder[-2::-1]:                             # for all blocks (except the source) in reverse postorder
                new_dom = set.intersection(*[ dom[p] for p in b.predecessors ]) | { b }
                if dom[b] != new_dom:
                    dom[b] = new_dom
                    changed = True

        idom = { self.blocks['entry'] : None }                      # idom[b] contains exactly one block, the immediate dominator of b
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

        variables = [ i.a for i in self.blocks['entry'].instructions if 'alloca' in i.str ]
        phi = { v:set() for v in variables }                        # map (variable -> set of basic blocks)
        for v in variables:
            blocks_with_store = { b for b in self.blocks.values() for i in b.instructions if 'store' in i.str and i.b==v }
            blocks_to_consider = blocks_with_store.copy()
            while blocks_to_consider:
                block = blocks_to_consider.pop()
                for frontier in self.df[block]:
                    phi[v].add(frontier)
                    if frontier not in blocks_with_store:
                        blocks_to_consider.add(frontier)

        for v, bb in phi.items():                                   # insert phi nodes (for the moment without choices)
            for b in bb:
                b.add_phi_function(v)

        def store_load(block, visited, stack):
            def find_variable(v, stack):                            # walk the stack back until
                for frame in reversed(stack):                       # the current variable instance is found
                    if v in frame: return frame[v]

            for v, phi in block.phi_functions.items():              # place phi node choice for the current path
                b, val = find_variable(v, stack)
                phi.choice[b] = val
                stack[-1][v] = (block.label, phi.reg)
            if block in visited: return                             # we need to revisit blocks with phi functions as many times as we have incoming edges,
            visited.add(block)                                      # therefore the visited check is made after the choice placement

            for i in block.instructions[:]:                         # iterate through a copy since we modify the list
                match i.str:
                    case _ if 'load' in i.str:
                        _, val = find_variable(i.b, stack)
                        block.instructions.remove(i)
                        block.replacements[i.a] = val
                    case _ if 'store' in i.str:
                        stack[-1][i.b] = (block.label, i.a)
                        block.instructions.remove(i)
                    case _ if 'br i1' in i.str:
                        stack.append({})
                        store_load(self.blocks[i.b], visited, stack)
                        stack.pop()
                        stack.append({})
                        store_load(self.blocks[i.c], visited, stack)
                        stack.pop()
                    case _ if 'br label' in i.str:
                        store_load(self.blocks[i.a],  visited, stack)
        stack = [{}] # stack of maps (variable -> (block, value)); necessary for storing context while branching
        store_load(self.blocks['entry'], set(), stack)

cfg = ControlFlowGraph()
cfg.add_block('entry')
cfg.add_block('bb1')
cfg.add_block('bb2')
cfg.add_block('bb3')
cfg.add_block('bb4')
cfg.add_block('bb5')
cfg.add_block('bb6')
cfg.add_block('bb7')
cfg.add_block('bb8')

cfg.blocks['entry'].instructions = [
    Instruction('\t{a} = alloca {t}', 'i32', '%a'),
    Instruction('\tbr label %{a}', None, 'bb1'),
]

cfg.blocks['bb1'].instructions = [
    Instruction('\tstore {t} {a}, {t}* {b}', 'i32', '1', '%a'),
    Instruction('\tbr i1 %{a}, label %{b}, label %{c}', None, 'foo', 'bb2', 'bb4'),
]

cfg.blocks['bb2'].instructions = [
    Instruction('\t{a} = load {t}, {t}* {b}', 'i32', '%a0', '%a'),
    Instruction('\t{a} = add {t} {b}, {c}', 'i32', '%t0', '%a0', '1'),
    Instruction('\tstore {t} {a}, {t}* {b}', 'i32', '%t0', '%a'),
    Instruction('\tbr label %{a}', None, 'bb3'),
]

cfg.blocks['bb3'].instructions = [
    Instruction('\t{a} = load {t}, {t}* {b}', 'i32', '%a1', '%a'),
    Instruction('\t{a} = add {t} {b}, {c}', 'i32', '%t1', '%a1', '%a1'),
    Instruction('\tstore {t} {a}, {t}* {b}', 'i32', '%t1', '%a'),
    Instruction('\tbr i1 %{a}, label %{b}, label %{c}', None, 'foo', 'bb8', 'bb2'),
]

cfg.blocks['bb4'].instructions = [
    Instruction('\tbr i1 %{a}, label %{b}, label %{c}', None, 'foo', 'bb5', 'bb6'),
]

cfg.blocks['bb5'].instructions = [
    Instruction('\t{a} = load {t}, {t}* {b}', 'i32', '%a2', '%a'),
    Instruction('\tstore {t} {a}, {t}* {b}', 'i32', '2', '%a'),
    Instruction('\tbr label %{a}', None, 'bb7'),
]

cfg.blocks['bb6'].instructions = [
    Instruction('\t{a} = load {t}, {t}* {b}', 'i32', '%a3', '%a'),
    Instruction('\tstore {t} {a}, {t}* {b}', 'i32', '3', '%a'),
    Instruction('\tbr label %{a}', None, 'bb7'),
]

cfg.blocks['bb7'].instructions = [
    Instruction('\t{a} = load {t}, {t}* {b}', 'i32', '%a4', '%a'),
    Instruction('\tbr label %{a}', None, 'bb8'),
]

cfg.blocks['bb8'].instructions = [
    Instruction('\t{a} = load {t}, {t}* {b}', 'i32', '%a5', '%a'),
    Instruction('\tret {a}', None, '%a5'),
]

print(cfg)
cfg.compute_adjacency()

cfg.mem2reg()

print(cfg)


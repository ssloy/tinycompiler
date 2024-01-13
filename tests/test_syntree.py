import pytest
import io, sys # for exec stdout redirection
from syntree import *
from transpy_naive import *

def test_syntree(tmp_path):
    abs_fun = Function('abs',       # function name
        [('x', {'type':Type.INT})], # one integer argument
        [],                         # no local variables
        [],                         # no nested functions
        [                           # function body
            IfThenElse(
                LogicOp('<', Var('x'), Integer(0)),           # if x < 0
                [Return(ArithOp('-', Integer(0), Var('x')))], # then return 0-x
                [Return(Var('x'))])                           # else return x
        ],
        {'type':Type.INT})          # return type

    sqrt_fun = Function('sqrt',                                      # function name
        [('n', {'type':Type.INT}), ('shift', {'type':Type.INT})],    # input fixed-point number (two integer variables)
        [
            ('x', {'type':Type.INT}),                                # three local integer variables
            ('x_old', {'type':Type.INT}),
            ('n_one', {'type':Type.INT})
        ],
        [],                                                         # no nested functions
        [                                                           # function body
            IfThenElse(
                LogicOp('>', Var('n'), Integer(65535)),             # if n > 65535
                [Return(ArithOp('*', Integer(2),                    #    return 2*sqrt(n/4)
                        FunCall('sqrt', [ArithOp('/', Var('n'), Integer(4)), Var('shift')])))],
                []),                                                # no else statements
            Assign('x', Var('shift')),                              # x = shift
            Assign('n_one', ArithOp('*', Var('n'), Var('shift'))),  # n_one = n*shift
            While(Boolean(True), [                                  # while true
                Assign('x_old', Var('x')),                          #     x_old = x
                Assign('x',                                         #     x = (x + n_one / x) / 2
                    ArithOp('/',
                        ArithOp('+',
                            Var('x'),
                            ArithOp('/', Var('n_one'), Var('x'))),
                        Integer(2))),
                IfThenElse(                                         #     if abs(x-x_old) <= 1
                    LogicOp('<=',
                        FunCall('abs', [ArithOp('-', Var('x'), Var('x_old'))]),
                        Integer(1)),
                    [Return(Var('x'))],                             #        return x
                    []),                                            #     no else statements
            ]),
        ],
        {'type':Type.INT})                                          # return type

    main_fun = Function('main', # function name
        [],                     # no arguments
        [],                     # no local variables
        [sqrt_fun, abs_fun],    # two nested functions
        [Print(                 # println sqrt(25735, 8192);
            FunCall('sqrt', [Integer(25735), Integer(8192)]),
            True)
        ],
        {'type':Type.VOID})     # return type

    program = transpy(main_fun)

    print(program) # save the output to a temp dir
    old_stdout = sys.stdout
    with open(tmp_path / 'sqrt.py', 'w') as output:
        sys.stdout = output
        print(program)
        sys.stdout = old_stdout
    old_stdout = sys.stdout

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    exec(program)
    result = sys.stdout.getvalue().strip()
    sys.stdout = old_stdout
    assert 14519 == int(result)


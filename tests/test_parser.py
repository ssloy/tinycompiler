import pytest
from lexer import WendLexer
from parser import WendParser
from syntree import *

def tree_signature(n):
    if isinstance(n, Function):
        return 'Function{%s,%s}' % (''.join([tree_signature(f) for f in n.fun]), ''.join([tree_signature(s) for s in n.body]))
    elif isinstance(n, Print):
        return 'Print{%s}' % tree_signature(n.expr)
    elif isinstance(n, Return):
        return 'Return{%s}' % tree_signature(n.expr)
    elif isinstance(n, Assign):
        return 'Assign{%s}' % tree_signature(n.expr)
    elif isinstance(n, FunCall):
        return 'FunCall{%s}' % ','.join([tree_signature(e) for e in n.args])
    elif isinstance(n, While):
        return 'While{%s,%s}' % (tree_signature(n.expr), ''.join([tree_signature(s) for s in n.body]))
    elif isinstance(n, IfThenElse):
        return 'IfThenElse{%s,%s,%s}' % (tree_signature(n.expr), ''.join([tree_signature(s) for s in n.ibody]), ''.join([tree_signature(s) for s in n.ebody]))
    elif isinstance(n, ArithOp):
        return 'ArithOp{%s,%s}' % (tree_signature(n.left), tree_signature(n.right))
    elif isinstance(n, LogicOp):
        return 'LogicOp{%s,%s}' % (tree_signature(n.left), tree_signature(n.right))
    elif isinstance(n, Integer):
        return 'Integer'
    elif isinstance(n, Boolean):
        return 'Boolean'
    elif isinstance(n, Var):
        return 'Var'
    elif isinstance(n, String):
        return 'String'
    return ''

@pytest.mark.parametrize(
    'program, expected_output, expected_signature', (
        ('fun main() {print +3 + 5 * -2;}', '-7', 'Function{,Print{ArithOp{Integer,ArithOp{Integer,ArithOp{Integer,Integer}}}}}'),
        ('fun main() {print 3 - 4 * 5;}', '-17', 'Function{,Print{ArithOp{Integer,ArithOp{Integer,Integer}}}}'),
        ('fun main() {print 3 - 10 / 5;}', '1', 'Function{,Print{ArithOp{Integer,ArithOp{Integer,Integer}}}}'),
        ('fun main() {print (-2+3*4)+5/(7-6)%8;}', '15', 'Function{,Print{ArithOp{ArithOp{ArithOp{Integer,Integer},ArithOp{Integer,Integer}},ArithOp{ArithOp{Integer,ArithOp{Integer,Integer}},Integer}}}}'),
        ('fun main() {print 5<3;}', 'False', 'Function{,Print{LogicOp{Integer,Integer}}}'),
        ('fun main() {print 3==3;}', 'True', 'Function{,Print{LogicOp{Integer,Integer}}}'),
        ('fun main() {print 3 * (4 + 5) / 7 == 3;}', 'True', 'Function{,Print{LogicOp{ArithOp{ArithOp{Integer,ArithOp{Integer,Integer}},Integer},Integer}}}'),
        ('fun main() {print true && false;}', 'False', 'Function{,Print{LogicOp{Boolean,Boolean}}}'),
        ('fun main() {print true && false || true;}', 'True', 'Function{,Print{LogicOp{LogicOp{Boolean,Boolean},Boolean}}}'),
        ('fun main() {print !true;}', 'False', 'Function{,Print{LogicOp{Boolean,Boolean}}}'),
        ('fun main() {print 3<=3 && 3>=3;}', 'True', 'Function{,Print{LogicOp{LogicOp{Integer,Integer},LogicOp{Integer,Integer}}}}'),
    )
)

def test_arithmetic(program, expected_output, expected_signature):
    assert tree_signature(WendParser().parse(WendLexer().tokenize(program))) == expected_signature

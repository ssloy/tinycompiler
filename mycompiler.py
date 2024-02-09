import io, sys
from lexer import *
from earley import WendParser
from syntree import *
from analyzer import *
from transasm import *


if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
if True:
#try:
    f = open(sys.argv[1], 'r')
    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)
#    print(tree_signature(ast))
    build_symtable(ast)
    print(transasm(ast))
#except Exception as e:
#    print(e)


import io, sys
from mylexer import tokenize
#from lexer import WendLexer
from parser import WendParser
from analyzer import *
from transasm import *

if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
try:
    f = open(sys.argv[1], 'r')
    tokens = tokenize(f.read())
    ast = WendParser().parse(tokens)
    build_symtable(ast)
    print(transasm(ast))
except Exception as e:
    print(e)


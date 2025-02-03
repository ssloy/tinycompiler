import io, sys
from lexer import WendLexer
from parser import WendParser
from analyzer import *
#from transasm import *
from transllvm import *

if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
if True:
    f = open(sys.argv[1], 'r')
    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)
    build_symtable(ast)
    print(transllvm(ast))
#except Exception as e:
#    print(e)

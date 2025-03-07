import io, sys
from lexer import WendLexer
from parser import WendParser
from analyzer import decorate
from transasm import transasm

if len(sys.argv)!=2:
    sys.exit('Usage: compiler.py path/source.wend')
try:
    f = open(sys.argv[1], 'r')
    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)
    decorate(ast)
    print(transasm(ast))
except Exception as e:
    print(e)

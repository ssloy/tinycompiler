import pytest
#import shutil
import io, sys
from lexer import WendLexer
from parser import WendParser
from transpy_naive import *

@pytest.mark.parametrize('test_case', (
        'helloworld', 'sqrt', 'fixed-point', 'scope', 'overload', 'mutual-recursion'
    )
)

def test_transpy(tmp_path, test_case):
    source_file     = test_case + '.wend'
    expected_output = test_case + '.expected'
    target_file     = test_case + '.py'
    f = open('test-data/' + source_file, 'r')

    tokens = WendLexer().tokenize(f.read())
    ast = WendParser().parse(tokens)

    program = transpy(ast)
    old_stdout = sys.stdout
    with open(tmp_path / target_file, 'w') as output:
        sys.stdout = output
        print(program)
        sys.stdout = old_stdout

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    exec(program)
    result = sys.stdout.getvalue().strip()
    sys.stdout = old_stdout
    with open('test-data/' + expected_output) as f:
        expected_result = f.read().strip()

    assert result == expected_result


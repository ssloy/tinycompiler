import pytest

@pytest.fixture
def lexer():
    from lexer import WendLexer
    return WendLexer()

@pytest.mark.parametrize(
    'test_string, expected_tokens', (
        ('{}', (
            ('BEGIN', '{'),
            ('END', '}')
        )),
        ('whilea=0;', (
            ('ID', 'whilea'),
            ('ASSIGN', '='),
            ('INTVAL', '0'),
            ('SEMICOLON', ';')
        )),
        ('3alpha:int', (
            ('INTVAL', '3'),
            ('ID', 'alpha'),
            ('COLON', ':'),
            ('INT', 'int')
        )),
        ('while=0;', (
            ('WHILE', 'while'),
            ('ASSIGN', '='),
            ('INTVAL', '0'),
            ('SEMICOLON', ';')
        )),

        ('''{
            println(02); // no direct conversion to integer values
            println "hello world";
            // println(3);
        }''', (
            ('BEGIN', '{'),
            ('PRINTLN', 'println'),
            ('LPAREN', '('),
            ('INTVAL', '02'),
            ('RPAREN', ')'),
            ('SEMICOLON', ';'),
            ('PRINTLN', 'println'),
            ('STRING', '"hello world"'),
            ('SEMICOLON', ';'),
            ('END', '}')
        )),

        ('a = 2;', (
            ('ID', 'a'),
            ('ASSIGN', '='),
            ('INTVAL', '2'),
            ('SEMICOLON', ';')
        )),

        ('(-2+3*4)+5/(7-6)%8', (
            ('LPAREN', '('),
            ('MINUS', '-'),
            ('INTVAL', '2'),
            ('PLUS', '+'),
            ('INTVAL', '3'),
            ('TIMES', '*'),
            ('INTVAL', '4'),
            ('RPAREN', ')'),
            ('PLUS', '+'),
            ('INTVAL', '5'),
            ('DIVIDE', '/'),
            ('LPAREN', '('),
            ('INTVAL', '7'),
            ('MINUS', '-'),
            ('INTVAL', '6'),
            ('RPAREN', ')'),
            ('MOD', '%'),
            ('INTVAL', '8')
        )),
    )
)

def test_lexer(lexer, test_string, expected_tokens):
    tokens = list(lexer.tokenize(test_string))
    assert len(tokens) == len(expected_tokens)
    for token, (expected_type, expected_value) in zip(tokens, expected_tokens):
        assert token.type  == expected_type
        assert token.value == expected_value

@pytest.mark.parametrize(
    'test_string, expected_message', (
        ('print "true;', 'Line 1: illegal character \'"\''),
    )
)

def test_lexer_err(lexer, test_string, expected_message):
    try:
        tokens = list(lexer.tokenize(test_string))
        assert False
    except Exception as e:
        assert str(e) == expected_message

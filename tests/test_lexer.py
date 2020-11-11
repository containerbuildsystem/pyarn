from ply import lex
import pytest

from pyarn import lexer


@pytest.mark.parametrize(
    'data, expected_types, expected_values',
    [
        ('foo "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('foo "bar"\n', ['STRING', 'STRING', 'NEWLINE'], ['foo', 'bar', '\n']),
        ('foo  "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('foo        "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('"foo" "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('"foo" "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        (
            'foo:\n  bar "bar"',
            ['STRING', 'COLON', 'NEWLINE', 'INDENT', 'STRING', 'STRING'],
            ['foo', ':', '\n', 1, 'bar', 'bar']
        ),
        (
            'foo:\n  bar:\n  foo "bar"',
            [*['STRING', 'COLON', 'NEWLINE', 'INDENT']*2, 'STRING', 'STRING'],
            ['foo', ':', '\n', 1, 'bar', ':', '\n', 1, 'foo', 'bar']
        ),
        (
            'foo:\n  bar:\n    foo "bar"',
            [*['STRING', 'COLON', 'NEWLINE', 'INDENT']*2, 'STRING', 'STRING'],
            ['foo', ':', '\n', 1, 'bar', ':', '\n', 2, 'foo', 'bar']
        ),
        (
            'foo:\r\n  bar:\r\n    foo "bar"',
            [*['STRING', 'COLON', 'NEWLINE', 'INDENT']*2, 'STRING', 'STRING'],
            ['foo', ':', '\r\n', 1, 'bar', ':', '\r\n', 2, 'foo', 'bar']
        ),
        (
            'foo:\n  bar:\n    yes no\nbar:\n  yes no',
            [
                *['STRING', 'COLON', 'NEWLINE', 'INDENT']*2, 'STRING', 'STRING', 'NEWLINE',
                'STRING', 'COLON', 'NEWLINE', 'INDENT', 'STRING', 'STRING'
            ],
            [
                'foo', ':', '\n', 1, 'bar', ':', '\n', 2, 'yes', 'no', '\n', 'bar', ':', '\n', 1,
                'yes', 'no',
            ],
        ),
        (
            'foo:\r\n  bar:\r\n    yes no\r\nbar:\r\n  yes no',
            [
                *['STRING', 'COLON', 'NEWLINE', 'INDENT']*2, 'STRING', 'STRING', 'NEWLINE',
                'STRING', 'COLON', 'NEWLINE', 'INDENT', 'STRING', 'STRING',
            ],
            [
                'foo', ':', '\r\n', 1, 'bar', ':', '\r\n', 2, 'yes', 'no', '\r\n', 'bar', ':',
                '\r\n', 1, 'yes', 'no',
            ]
        ),
        (
            'foo:\n\n\n  bar "bar"\n',
            ['STRING', 'COLON', 'NEWLINE', 'INDENT', 'STRING', 'STRING', 'NEWLINE'],
            ['foo', ':', '\n\n\n', 1, 'bar', 'bar', "\n"]
        ),
    ],
)
def test_lexer(data, expected_types, expected_values):
    if len(expected_types) != len(expected_values):
        msg = f'Length of parameters should match for [{expected_types}, {expected_values}]'
        raise ValueError(msg)
    # Adjust for t_eof behavior
    if expected_types[-1] != 'NEWLINE':
        expected_types.append('NEWLINE')
        expected_values.append('\n')

    test_lexer = lex.lex(module=lexer)
    test_lexer.input(data)
    tokens = list(test_lexer)
    for token, expected_type, expected_value in zip(tokens, expected_types, expected_values):
        assert token.type == expected_type
        assert token.value == expected_value

    assert len(tokens) == len(expected_types)


@pytest.mark.parametrize(
    'data, error',
    [
        ('@', '1: Invalid token @'),
        ('foo:\n\tbar', '2: Invalid token \tbar'),
    ]
)
def test_lexer_error(data, error):
    test_lexer = lex.lex(module=lexer)
    test_lexer.input(data)
    with pytest.raises(ValueError) as exc:
        list(test_lexer)[0]
        test_lexer.input(data)
    assert str(exc.value) == error


def test_lexer_lineno():
    data = 'foo\nbar\n\nbaz end'
    test_lexer = lex.lex(module=lexer)
    test_lexer.input(data)
    tokens = list(test_lexer)
    assert (tokens[0].value, tokens[0].lineno) == ("foo", 1)
    assert (tokens[2].value, tokens[2].lineno) == ("bar", 2)
    assert (tokens[4].value, tokens[4].lineno) == ("baz", 4)
    assert (tokens[5].value, tokens[5].lineno) == ("end", 4)

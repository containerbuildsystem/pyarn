import os

from ply import lex, yacc
import pytest

from pyarn import lexer, parser


@pytest.mark.parametrize(
    'data, expected_result',
    [
        ('foo "bar"', {'foo': 'bar'}),
        ('foo "bar"\n', {'foo': 'bar'}),
        ('foo  "bar"', {'foo': 'bar'}),
        ('foo        "bar"', {'foo': 'bar'}),
        ('"foo" "bar"', {'foo': 'bar'}),
        ('"foo" "bar"', {'foo': 'bar'}),
        ('foo:\n  bar "bar"', {'foo': {'bar': 'bar'}}),
        ('foo:\n  bar:\n    foo "bar"', {'foo': {'bar': {'foo': 'bar'}}}),
        ('foo:\r\n  bar:\r\n    foo "bar"', {'foo': {'bar': {'foo': 'bar'}}}),
        (
            'foo:\n  bar:\n    yes no\nbar:\n  yes no',
            {'foo': {'bar': {'yes': 'no'}}, 'bar': {'yes': 'no'}},
        ),
        (
            'foo:\r\n  bar:\r\n    yes no\r\nbar:\r\n  yes no',
            {'foo': {'bar': {'yes': 'no'}}, 'bar': {'yes': 'no'}}
        ),
        ('foo:\n\n\n  bar "bar"\n', {'foo': {'bar': 'bar'}}),
    ],
)
def test_parser(data, expected_result):
    lex.lex(module=lexer)
    test_parser = yacc.yacc(module=parser)
    result = test_parser.parse(data, debug=False)
    assert result == expected_result


def test_regressions():
    lex.lex(module=lexer)
    test_parser = yacc.yacc(module=parser)

    tests_dir = os.path.dirname(__file__)
    test_data_dir = os.path.join(tests_dir, 'data')
    test_data = os.listdir(test_data_dir)
    test_files = [
        os.path.join(test_data_dir, f) for f in test_data
        if os.path.isfile(os.path.join(test_data_dir, f))
    ]
    for test_file in test_files:
        with open(test_file, 'r') as tf:
            data = tf.read()
        test_parser.parse(data, debug=False)

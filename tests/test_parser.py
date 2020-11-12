"""
Copyright (C) 2020  Red Hat, Inc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os

from ply import lex, yacc
import pytest

from pyarn import lexer, parser
from pyarn.indent_lexer import Wrapper


@pytest.mark.parametrize(
    'data, expected_result',
    [
        ('# just a comment\n', {'data': {}, 'comments': ['# just a comment']}),
        ('# another comment', {'data': {}, 'comments': ['# another comment']}),
        ('# two\n# comments\n', {'data': {}, 'comments': ['# two', '# comments']}),
        ('foo "bar"', {'data': {'foo': 'bar'}, 'comments': []}),
        ('foo "bar"\n', {'data': {'foo': 'bar'}, 'comments': []}),
        ('# comment\nfoo "bar"\n', {'data': {'foo': 'bar'}, 'comments': ['# comment']}),
        ('foo "bar"\n# a comment\n', {'data': {'foo': 'bar'}, 'comments': ["# a comment"]}),
        ('foo  "bar"', {'data': {'foo': 'bar'}, 'comments': []}),
        ('foo        "bar"', {'data': {'foo': 'bar'}, 'comments': []}),
        ('"foo" "bar"', {'data': {'foo': 'bar'}, 'comments': []}),
        ('"foo" "bar"', {'data': {'foo': 'bar'}, 'comments': []}),
        ('foo:\n  bar "bar"', {'data': {'foo': {'bar': 'bar'}}, 'comments': []}),
        ('foo:\n  bar:\n    foo "bar"', {'data': {'foo': {'bar': {'foo': 'bar'}}}, 'comments': []}),
        (
            'foo:\r\n  bar:\r\n    foo "bar"',
            {'data': {'foo': {'bar': {'foo': 'bar'}}}, 'comments': []}
        ),
        (
            'foo:\n  bar:\n    yes no\nbar:\n  yes no',
            {'data': {'foo': {'bar': {'yes': 'no'}}, 'bar': {'yes': 'no'}}, 'comments': []},
        ),
        (
            'foo:\r\n  bar:\r\n    yes no\r\nbar:\r\n  yes no',
            {'data': {'foo': {'bar': {'yes': 'no'}}, 'bar': {'yes': 'no'}}, 'comments': []}
        ),
        ('foo:\n\n\n  bar "bar"\n', {'data': {'foo': {'bar': 'bar'}}, 'comments': []}),
        # test nested structures
        ('a:\n  b: \n    c d', {'data': {'a': {'b': {'c': 'd'}}}, 'comments': []}),
        ('a:\n  b: \n    c d\n  e f', {'data': {'a': {'b': {'c': 'd'}, 'e': 'f'}}, 'comments': []}),
    ],
)
def test_parser(data, expected_result):
    lex_wrapper = Wrapper(lex.lex(module=lexer))
    test_parser = yacc.yacc(module=parser)
    result = test_parser.parse(data, lexer=lex_wrapper)
    assert result == expected_result


@pytest.mark.parametrize(
    'data',
    [
        # wrong indentation
        ('foo:\n  bar:\n  foo "bar"'),
    ],
)
def test_parser_error(data):
    lex_wrapper = Wrapper(lex.lex(module=lexer))
    test_parser = yacc.yacc(module=parser)
    with pytest.raises(ValueError):
        test_parser.parse(data, lexer=lex_wrapper)


def test_regressions():
    lex_wrapper = Wrapper(lex.lex(module=lexer))
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
        test_parser.parse(data, lexer=lex_wrapper)

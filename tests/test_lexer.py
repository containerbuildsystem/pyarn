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
from ply import lex
import pytest

from pyarn import lexer


@pytest.mark.parametrize(
    'data, expected_types, expected_values',
    [
        ('foo "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('foo "bar"\n', ['STRING', 'STRING'], ['foo', 'bar']),
        ('foo  "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('foo        "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('"foo" "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        ('"foo" "bar"', ['STRING', 'STRING'], ['foo', 'bar']),
        (
            'foo:\n  bar "bar"',
            ['STRING', 'COLON', 'INDENT', 'STRING', 'STRING', 'DEDENT'],
            ['foo', ':', 1, 'bar', 'bar', 1]
        ),
        (
            'foo:\n  bar:\n  foo "bar"',
            ['STRING', 'COLON', 'INDENT', 'STRING', 'COLON', 'STRING', 'STRING', 'DEDENT'],
            ['foo', ':', 1, 'bar', ':', 'foo', 'bar', 1]
        ),
        (
            'foo:\n  bar:\n    foo "bar"',
            [*['STRING', 'COLON', 'INDENT']*2, 'STRING', 'STRING', 'DEDENT'],
            ['foo', ':', 1, 'bar', ':', 2, 'foo', 'bar', 2]
        ),
        (
            'foo:\r\n  bar:\r\n    foo "bar"',
            [*['STRING', 'COLON', 'INDENT']*2, 'STRING', 'STRING', 'DEDENT'],
            ['foo', ':', 1, 'bar', ':', 2, 'foo', 'bar', 2]
        ),
        (
            'foo:\n  bar:\n    yes no\nbar:\n  yes no',
            [
                *['STRING', 'COLON', 'INDENT']*2, 'STRING', 'STRING', 'DEDENT',
                'STRING', 'COLON', 'INDENT', 'STRING', 'STRING', 'DEDENT'
            ],
            [
                'foo', ':', 1, 'bar', ':', 2, 'yes', 'no', 2, 'bar', ':',  1,
                'yes', 'no', 1
            ],
        ),
        (
            'foo:\r\n  bar:\r\n    yes no\r\nbar:\r\n  yes no',
            [
                *['STRING', 'COLON', 'INDENT']*2, 'STRING', 'STRING', 'DEDENT',
                'STRING', 'COLON', 'INDENT', 'STRING', 'STRING', 'DEDENT'
            ],
            [
                'foo', ':', 1, 'bar', ':', 2, 'yes', 'no', 2, 'bar', ':',  1,
                'yes', 'no', 1
            ],
        ),
        (
            'foo:\n\n\n  bar "bar"\n',
            ['STRING', 'COLON', 'INDENT', 'STRING', 'STRING', 'DEDENT'],
            ['foo', ':', 1, 'bar', 'bar', 1]
        ),
        ('foo 1', ['STRING', 'NUMBER'], ['foo', 1]),
        ('foo 42', ['STRING', 'NUMBER'], ['foo', 42]),
        (
            'foo:\n  answer 42', ['STRING', 'COLON', 'INDENT', 'STRING', 'NUMBER', 'DEDENT'],
            ['foo', ':', 1, 'answer', 42, 1]
        ),
        ('foo true', ['STRING', 'BOOLEAN'], ['foo', True]),
        ('foo "false"', ['STRING', 'STRING'], ['foo', 'false']),
        ('foo false', ['STRING', 'BOOLEAN'], ['foo', False]),
        ('foo "true"', ['STRING', 'STRING'], ['foo', 'true']),
        ('foo:bar:', ['STRING', 'COLON', 'STRING', 'COLON'], ['foo', ':', 'bar', ':']),
        ('"foo:bar":', ['STRING', 'COLON'], ['foo:bar', ':']),
        ('true false', ['BOOLEAN', 'BOOLEAN'], [True, False]),
        ('true-false', ['BOOLEAN', 'STRING'], [True, '-false']),
        ('not-true', ['STRING'], ['not-true']),
    ],
)
def test_lexer(data, expected_types, expected_values):
    if len(expected_types) != len(expected_values):
        msg = f'Length of parameters should match for [{expected_types}, {expected_values}]'
        raise ValueError(msg)

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
    assert (tokens[0].value, tokens[0].lineno) == ('foo', 1)
    assert (tokens[1].value, tokens[1].lineno) == ('bar', 2)
    assert (tokens[2].value, tokens[2].lineno) == ('baz', 4)
    assert (tokens[3].value, tokens[3].lineno) == ('end', 4)

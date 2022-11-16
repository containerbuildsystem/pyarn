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
import pytest
from ply import lex

from pyarn import lexer
from pyarn.lexer_wrapper import Wrapper


@pytest.mark.parametrize(
    "data, expected_types, expected_values",
    [
        (
            'foo:\n  bar:\n    foo "bar"',
            [
                *["STRING", "COLON", "INDENT"] * 2,
                "STRING",
                "STRING",
                "DEDENT",
                "DEDENT",
            ],
            ["foo", ":", 1, "bar", ":", 2, "foo", "bar", 1, 1],
        ),
        (
            'foo:\r\n  bar:\r\n    foo "bar"',
            [
                *["STRING", "COLON", "INDENT"] * 2,
                "STRING",
                "STRING",
                "DEDENT",
                "DEDENT",
            ],
            ["foo", ":", 1, "bar", ":", 2, "foo", "bar", 1, 1],
        ),
        (
            "foo:\n  bar:\n    yes no\nbar:\n  yes no",
            [
                *["STRING", "COLON", "INDENT"] * 2,
                "STRING",
                "STRING",
                "DEDENT",
                "DEDENT",
                "STRING",
                "COLON",
                "INDENT",
                "STRING",
                "STRING",
                "DEDENT",
            ],
            [
                "foo",
                ":",
                1,
                "bar",
                ":",
                2,
                "yes",
                "no",
                1,
                1,
                "bar",
                ":",
                1,
                "yes",
                "no",
                1,
            ],
        ),
        (
            "foo:\r\n  bar:\r\n    yes no\r\nbar:\r\n  yes no",
            [
                *["STRING", "COLON", "INDENT"] * 2,
                "STRING",
                "STRING",
                "DEDENT",
                "DEDENT",
                "STRING",
                "COLON",
                "INDENT",
                "STRING",
                "STRING",
                "DEDENT",
            ],
            [
                "foo",
                ":",
                1,
                "bar",
                ":",
                2,
                "yes",
                "no",
                1,
                1,
                "bar",
                ":",
                1,
                "yes",
                "no",
                1,
            ],
        ),
    ],
)
@pytest.mark.parametrize("use_iterator", [True, False])
def test_wrapper(data, expected_types, expected_values, use_iterator):
    if len(expected_types) != len(expected_values):
        msg = f"Length of parameters should match for [{expected_types}, {expected_values}]"
        raise ValueError(msg)

    test_lexer = Wrapper(lex.lex(module=lexer))
    test_lexer.input(data)
    tokens = []
    if use_iterator:
        tokens = list(test_lexer)
    else:
        while True:
            t = test_lexer.token()
            if not t:
                break
            tokens.append(t)

    for token, expected_type, expected_value in zip(tokens, expected_types, expected_values):
        assert token.type == expected_type
        assert token.value == expected_value

    assert len(tokens) == len(expected_types)

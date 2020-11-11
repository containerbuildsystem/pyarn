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
from pyarn.lexer import tokens  # noqa: F401


def p_blocks(p):
    """blocks : block
              | blocks block"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {**p[1], **p[2]}


def p_block(p):
    """block : title members
             | pair
             | comment"""
    if len(p) == 2:
        if isinstance(p[1], dict):
            # is pair
            p[0] = p[1]
        else:
            # TODO: handle comments
            p[0] = {"pyarn-comment": p[1]}
    else:
        # TODO: do we want to separate titles like "foo, bar"?
        # have in mind they may also be like "foo || bar, biz"
        p[0] = {p[1]: p[2]}


def p_title(p):
    """title : STRING COLON NEWLINE INDENT
             | list COLON NEWLINE INDENT"""
    p[0] = p[1]


def p_list(p):
    """list : STRING COMMA STRING
            | list COMMA STRING"""
    p[0] = ', '.join([p[1], p[3]])


def p_members(p):
    """members : pair
               | pair INDENT members
               | title members"""
    if len(p) == 2:
        p[0] = p[1]
    elif isinstance(p[1], str):  # titles
        p[0] = {p[1]: p[2]}
    elif isinstance(p[1], dict):  # pairs
        p[0] = {**p[1], **p[3]}
    else:
        raise SyntaxError(
            f'Error on reducing "members". "{p[1]}" should be str or dict, not {type(p[1])}'
        )


def p_pair(p):
    """pair : STRING STRING NEWLINE
            | STRING COLON STRING NEWLINE"""
    if len(p) == 4:
        p[0] = {p[1]: p[2]}
    else:
        p[0] = {p[1]: p[3]}


# TODO: handle indented comments
# this generates a parser conflict if not properly handled inside a block
def p_comment(p):
    """comment : COMMENT NEWLINE"""
    p[0] = "Just a comment"


def p_error(p):
    raise ValueError(f"error parsing {p}")

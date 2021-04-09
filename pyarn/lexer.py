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
tokens = (
    'STRING',
    'COMMENT',
    'COMMA',
    'COLON',
    'INDENT',
    'DEDENT',
    'NUMBER',
    'BOOLEAN',
)

t_COMMA = r','
t_COLON = r':'


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


# Note: this must be defined BEFORE t_STRING, the grammar is ambiguous
def t_BOOLEAN(t):
    r'true|false'
    t.value = (t.value == 'true')
    return t


# Unquoted string regex (see t_STRING)
# Docstrings cannot use string interpolation, this value is used by other modules
UNQUOTED_STRING = r'[a-zA-Z/.-][^\s\n,:]*'


# TODO: handle final escaped quotes
# Do this first to catch strings with spaces within
def t_STRING(t):
    r'"[^"\n]*"|[a-zA-Z/.-][^\s\n,:]*'
    if t.value.startswith('"'):
        t.value = t.value[1:-1]
    return t


def t_INDENT(t):
    r'(\n|\r\n)(?P<indent>([ ][ ])+)?'
    t.lexer.lineno += 1
    t.lexer.indent_lvl = getattr(t.lexer, 'indent_lvl', 0)
    raw_indent = t.lexer.lexmatch.groupdict().get('indent') or ''
    indents = len(raw_indent)//2
    if indents > t.lexer.indent_lvl:
        if indents != t.lexer.indent_lvl + 1:
            # no one line multiple indentation allowed
            raise SyntaxError
        t.lexer.indent_lvl = indents
        t.value = indents
        t.lexer.is_indented = True
        return t

    elif indents < t.lexer.indent_lvl:
        t.value = t.lexer.indent_lvl - indents
        t.lexer.indent_lvl = indents
        t.type = 'DEDENT'
        if t.lexer.indent_lvl == 0:
            t.lexer.is_indented = False
        return t


def t_spaces(t):
    r'[ ]'


def t_COMMENT(t):
    r'[#]+.*'
    return t


def t_eof(t):
    if getattr(t.lexer, 'is_indented', False):
        t.lexer.input('\n')
        return t.lexer.token()


def t_error(t):
    raise ValueError(f'{t.lexer.lineno}: Invalid token {t.value}')

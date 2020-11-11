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
    "STRING",
    "COMMENT",
    "COMMA",
    "COLON",
    "INDENT",
    "NEWLINE",
)

t_COMMENT = r"[#]+.*"
t_COMMA = r","
t_COLON = r":"


# TODO: handle final escaped quotes
# Do this first to catch strings with spaces within
def t_STRING(t):
    r'"[^"\n]*"|[a-zA-Z/.-]([^\s\n,]*[^\s\n,:])?'
    if t.value.startswith('"'):
        t.value = t.value[1:-1]
    t.lexer.is_new_line = False
    return t


def t_NEWLINE(t):
    r"(\n|\r\n)+"
    t.lexer.lineno += len(t.value)
    t.lexer.is_new_line = True
    return t


def t_INDENT(t):
    r"([ ][ ])+"
    if t.lexer.is_new_line:
        t.value = len(t.value)//2
        t.lexer.is_new_line = False
        return t


def t_spaces(t):
    r"[ ]"
    t.lexer.is_new_line = False


def t_eof(t):
    if not getattr(t.lexer, 'is_new_line', False):
        t.lexer.input('\n')
        return t.lexer.token()


def t_error(t):
    raise ValueError(f"{t.lexer.lineno}: Invalid token {t.value}")

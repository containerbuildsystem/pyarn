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


class Dedent():
    def __init__(self):
        self.type = 'DEDENT'
        self.value = 1


class Wrapper():
    def __init__(self, lexer):
        self.stack = []
        self.lexer = lexer

    def input(self, *args, **kwargs):
        self.lexer.input(*args, **kwargs)

    def token(self):
        if self.stack:
            return self.stack.pop()
        t = self.lexer.token()
        if t is None:
            return t

        if t.type != 'DEDENT':
            return t

        while t.value > 1:
            self.stack.append(Dedent())
            t.value -= 1

        return t

    def __iter__(self):
        i = True
        while i:
            r = self.token()
            if not r:
                i = False
            else:
                yield r

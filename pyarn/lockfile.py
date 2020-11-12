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
import re

import json

from ply import lex, yacc
from pyarn import lexer, parser
from pyarn.indent_lexer import Wrapper


class Lockfile():
    def __init__(self, version, data):
        self.version = version
        self.data = data
        if self.version == 'unknown':
            # TODO: log warning
            pass
        elif self.version != '1':
            raise ValueError(f'Unsupported yarn.lockfile version: {version}')

    def to_json(self):
        return json.dumps(self.data, sort_keys=True, indent=4)

    @classmethod
    def from_file(cls, path):
        with open(path) as lockfile:
            lockfile_str = lockfile.read()
        return Lockfile.from_str(lockfile_str)

    @classmethod
    def from_str(cls, lockfile_str):
        pyarn_lexer = Wrapper(lex.lex(module=lexer))
        lockfile_parser = yacc.yacc(module=parser)
        parsed_data = lockfile_parser.parse(lockfile_str, lexer=pyarn_lexer)
        version = 'unknown'
        for comment in parsed_data['comments']:
            declared_version = re.match(r'^# yarn lockfile v(\d+)$', comment)
            if declared_version:
                version = declared_version.group(1)
        return cls(version, parsed_data['data'])

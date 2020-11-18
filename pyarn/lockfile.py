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
import json
import logging
import re

from ply import lex, yacc
from pyarn import lexer, parser
from pyarn.lexer_wrapper import Wrapper


logger = logging.getLogger(__name__)


class Package():
    def __init__(self, name, version, url=None, checksum=None, relpath=None):
        if not name:
            raise ValueError('Package name was not provided')

        if not version:
            raise ValueError('Package version was not provided')

        self.name = name
        self.version = version
        self.url = url
        self.checksum = checksum
        self.relpath = relpath

    @classmethod
    def from_dict(cls, raw_name, data):
        raw_matcher = re.match(r'(?P<name>@?[^@]+)(?:@file:(?P<path>.+))?', raw_name)
        name = raw_matcher.groupdict()['name']
        path = raw_matcher.groupdict()['path']
        pkg = cls(
            name, data.get('version'), url=data.get('resolved'),
            checksum=data.get('integrity'), relpath=path
        )
        return pkg


class Lockfile():
    def __init__(self, version, data):
        self.version = version
        self.data = data
        if self.version == 'unknown':
            logger.warning('Unknown Yarn version. Was this lockfile manually edited?')
        elif self.version != '1':
            raise ValueError(f'Unsupported yarn.lockfile version: {version}')

    def to_json(self):
        return json.dumps(self.data, sort_keys=True, indent=4)

    def packages(self):
        packages = []
        for name, pkg_data in self.data.items():
            pkg = Package.from_dict(name, pkg_data)
            packages.append(pkg)
        return packages

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

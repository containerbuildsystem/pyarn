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
import io
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional, Pattern

from ply import lex, yacc

from pyarn import lexer, parser
from pyarn.lexer_wrapper import Wrapper

logger = logging.getLogger(__name__)

UNQUOTED_STRING_RE = re.compile(lexer.UNQUOTED_STRING)

V1_VERSION_COMMENT = "# yarn lockfile v1"


class Package:
    def __init__(
        self,
        name: str,
        version: str,
        url: Optional[str] = None,
        checksum: Optional[str] = None,
        path: Optional[str] = None,
        relpath: Optional[str] = None,
        dependencies: Optional[Dict[str, str]] = None,
        alias: Optional[str] = None,
    ) -> None:
        if not name:
            raise ValueError("Package name was not provided")

        if not version:
            raise ValueError("Package version was not provided")

        self.name = name
        self.version = version
        self.url = url
        self.checksum = checksum
        self.path = path if path is not None else relpath
        self.dependencies = dependencies or {}
        self.alias = alias

    @property
    def relpath(self) -> Optional[str]:
        """
        Return the path to the package.

        This is strictly kept for backwards compatibility and path should be used directly
        instead. The path is not always relative and may be absolute.
        """
        return self.path

    @relpath.setter
    def relpath(self, path: Optional[str]) -> None:
        """
        Set the path to the package.

        This is strictly kept for backwards compatibility and path should be used directly
        instead. The path is not always relative and may be absolute.
        """
        self.path = path

    @classmethod
    def from_dict(cls, raw_name: str, data: Dict[str, Any]) -> "Package":
        name_at_version = re.compile(r"(?P<name>@?[^@]+)(?:@(?P<version>[^,]*))?")

        # _version is the version as declared in package.json, not the resolved version
        name, _version = _must_match(name_at_version, raw_name).groups()
        alias = None
        path = None

        if _version and _version.startswith("npm:"):
            alias = name
            name, _version = _must_match(name_at_version, _remove_prefix(_version, "npm:")).groups()

        if _version:
            path = cls.get_path_from_version_specifier(_version)

        # Ensure the resolved version key exists to appease mypy
        version = data.get("version")
        if not version:
            raise ValueError("Package version was not provided")

        return cls(
            name=name,
            version=version,
            url=data.get("resolved"),
            checksum=data.get("integrity"),
            path=path,
            dependencies=data.get("dependencies", {}),
            alias=alias,
        )

    @staticmethod
    def get_path_from_version_specifier(version: str) -> Optional[str]:
        """Return the path from a package.json file dependency version specifier."""
        version_path = Path(version)

        if version.startswith("file:"):
            return _remove_prefix(version, "file:")
        elif version.startswith("link:"):
            return _remove_prefix(version, "link:")
        elif version_path.is_absolute() or version.startswith(("./", "../")):
            return str(version_path)
        else:
            # Some non-path version specifier, (e.g. "1.0.0" or a web link)
            # See https://docs.npmjs.com/cli/v10/configuring-npm/package-json#dependencies
            return None


def _remove_prefix(s: str, prefix: str) -> str:
    return s[len(prefix) :]


def _must_match(pat: Pattern, s: str) -> re.Match:
    match = pat.match(s)
    if not match:
        raise ValueError(f"Unexpected format: {s!r} (does not match {pat.pattern})")
    return match


class Lockfile:
    def __init__(self, version, data):
        self.version = version
        self.data = data

        if self.version == "unknown":
            logger.warning("Unknown Yarn version. Was this lockfile manually edited?")

        elif self.version != "1":
            raise ValueError(f"Unsupported yarn.lockfile version: {version}")

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
        lockfile_parser = yacc.yacc(module=parser, debug=False)
        parsed_data = lockfile_parser.parse(lockfile_str, lexer=pyarn_lexer)
        version = "unknown"
        for comment in parsed_data["comments"]:
            if comment == V1_VERSION_COMMENT:
                version = "1"
        return cls(version, parsed_data["data"])

    def to_file(self, path):
        with open(path, "w") as lockfile:
            self._dump(lockfile)

    def to_str(self):
        buffer = io.StringIO()
        self._dump(buffer)
        return buffer.getvalue()

    def _dump(self, outfile):
        # Does not preserve any comments, but this one is required
        outfile.write(V1_VERSION_COMMENT)
        outfile.write("\n")
        for key, val in self.data.items():
            # Separate top-level keyvals by newline
            outfile.write("\n")
            _dump_keyval(key, val, outfile, 0)


def _dump_keyval(key, value, outfile, indent_level):
    outfile.write(" " * indent_level * 2)
    outfile.write(_quote_key_if_needed(key))

    if isinstance(value, dict):
        outfile.write(":\n")
        for k, v in value.items():
            _dump_keyval(k, v, outfile, indent_level + 1)
        # No newline here, _dump_keyval has already added one (recursion always ends
        # with a string, integer or boolean - the grammar does not allow empty dicts)
    else:
        outfile.write(" ")
        if isinstance(value, str):
            # Always quote string values
            # TODO: use json.dump to quote the value instead
            #   (the lexer would also have to interpret strings using json.load)
            outfile.write(f'"{value}"')
        else:
            json.dump(value, outfile)
        outfile.write("\n")


def _quote_key_if_needed(key):
    # The key may be a comma-separated list of keys
    keys = map(str.strip, key.split(","))
    # TODO: quote keys properly, see TODO about quoting values
    return ", ".join(f'"{k}"' if _needs_quoting(k) else k for k in keys)


def _needs_quoting(s):
    if s.startswith("true") or s.startswith("false"):
        # If a string starts with a boolean, it must be quoted no matter what
        #   (otherwise, the string would be tokenized as BOOLEAN STRING)
        return True
    return UNQUOTED_STRING_RE.fullmatch(s) is None

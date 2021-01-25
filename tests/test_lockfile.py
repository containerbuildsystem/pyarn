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
import os
from textwrap import dedent

import pytest

from pyarn import lockfile


@pytest.mark.parametrize(
    'data, expected_data',
    [
        ('# comment\n', {}),
        ('foo "bar"', {'foo': 'bar'}),
        ('foo "bar"\n# comment\n', {'foo': 'bar'}),
        ('foo "bar"\n# comment', {'foo': 'bar'}),
    ]
)
def test_from_str(data, expected_data):
    lock = lockfile.Lockfile.from_str(data)
    assert lock.data == expected_data


def test_from_file():
    file_name = 'single.lock'
    expected = {
        'abab@^2.0.0': {
            'version': '2.0.0',
            'resolved': (
                'https://registry.yarnpkg.com/abab/-/abab-2.0.0.tgz#'
                'aba0ab4c5eee2d4c79d3487d85450fb2376ebb0f'
            ),
            'integrity': (
                'sha512-sY5AXXVZv4Y1VACTtR11UJCPHHudgY5i26Qj5TypE6DKlIApbwb5uqhXcJ5UUGbvZNRh7EeIoW+'
                'LrJumBsKp7w=='
            )
        }
    }
    tests_dir = os.path.dirname(__file__)
    test_data_dir = os.path.join(tests_dir, 'data')
    test_file = os.path.join(test_data_dir, file_name)
    lock = lockfile.Lockfile.from_file(test_file)
    assert lock.data == expected


def test_v1():
    lock = lockfile.Lockfile.from_str('# yarn lockfile v1\n')
    assert lock.version == '1'


def test_no_version(caplog):
    lockfile.Lockfile.from_str('# comment\n')
    assert 'Unknown Yarn version. Was this lockfile manually edited?' in caplog.text


@pytest.mark.parametrize('data', [('# comment\n'), ('foo "bar"'), ('foo "bar"\n# comment\n')])
def test_unknown_version(data):
    lock = lockfile.Lockfile.from_str(data)
    assert lock.version == 'unknown'


def test_invalid_version():
    with pytest.raises(ValueError, match="Unsupported yarn.lockfile version: 2"):
        # Currently, the only way to specify an invalid version is by initializing directly
        lockfile.Lockfile('2', {})


@pytest.mark.parametrize(
    'data, expected_data',
    [
        ('# comment\n', {}),
        ('foo "bar"', {'foo': 'bar'}),
        ('foo "bar"\n# comment\n', {'foo': 'bar'}),
        ('foo "bar"\n# comment', {'foo': 'bar'}),
    ]
)
def test_to_json(data, expected_data):
    lock = lockfile.Lockfile.from_str(data)
    assert lock.to_json() == json.dumps(expected_data, sort_keys=True, indent=4)


def test_packages():
    data = 'breakfast@^1.1.1:\n  eggs bacon\n  version "2.0.0"'
    lock = lockfile.Lockfile.from_str(data)
    packages = lock.packages()
    assert len(packages) == 1
    assert packages[0].name == 'breakfast'
    assert packages[0].version == '2.0.0'
    assert packages[0].checksum is None
    assert packages[0].url is None
    assert packages[0].relpath is None


def test_packages_no_version():
    data = 'breakfast@^1.1.1:\n  eggs bacon'
    lock = lockfile.Lockfile.from_str(data)
    with pytest.raises(ValueError, match='Package version was not provided'):
        lock.packages()


def test_packages_no_name():
    with pytest.raises(ValueError, match='Package name was not provided'):
        lockfile.Package(None, '1.0.0')


def test_packages_url():
    url = 'https://example.com/breakfast/1.1.1.tar.gz'
    data = f'breakfast@^1.1.1:\n  version "2.0.0"\n  resolved "{url}"'
    lock = lockfile.Lockfile.from_str(data)
    packages = lock.packages()
    assert len(packages) == 1
    assert packages[0].name == 'breakfast'
    assert packages[0].version == '2.0.0'
    assert packages[0].checksum is None
    assert packages[0].url == url
    assert packages[0].relpath is None


def test_packages_checksum():
    url = 'https://example.com/breakfast/1.1.1.tar.gz'
    data = f'breakfast@^1.1.1:\n  version "2.0.0"\n  resolved "{url}"\n  integrity someHash'
    lock = lockfile.Lockfile.from_str(data)
    packages = lock.packages()
    assert len(packages) == 1
    assert packages[0].name == 'breakfast'
    assert packages[0].version == '2.0.0'
    assert packages[0].checksum == 'someHash'
    assert packages[0].url == url
    assert packages[0].relpath is None


def test_relpath():
    data = '"breakfast@file:some/relative/path":\n  version "0.0.0"'
    lock = lockfile.Lockfile.from_str(data)
    packages = lock.packages()
    assert len(packages) == 1
    assert packages[0].name == 'breakfast'
    assert packages[0].version == '0.0.0'
    assert packages[0].checksum is None
    assert packages[0].url is None
    assert packages[0].relpath == 'some/relative/path'


def test_package_with_comma():
    data = 'eggs@^1.1.1, eggs@^1.1.2, eggs@^1.1.3:\n  version "1.1.7"'
    lock = lockfile.Lockfile.from_str(data)
    packages = lock.packages()
    assert len(packages) == 1
    assert packages[0].name == 'eggs'
    assert packages[0].version == '1.1.7'
    assert packages[0].checksum is None
    assert packages[0].url is None
    assert packages[0].relpath is None


DATA_TO_DUMP = {
    'foo@^1.0.0': {
        'version': '1.0.0',
        'resolved': 'https://registry.yarnpkg.com/foo/-/foo-1.0.0.tgz',
        'dependencies': {
            'bar': '^2.0.0'
        },
        'some number': 1,
    },
    'bar@^2.0.0': {
        'version': '2.0.0',
        'resolved': 'https://registry.yarnpkg.com/bar/-/bar-2.0.0.tgz',
        'some boolean': True,
    },
    'baz@https://example.org/baz.tar.gz': {
        'version': '3.0.0',
        'resolved': 'https://example.org/baz.tar.gz',
    },
    'spam@^4.0.0, spam@^4.0.1': {
        'version': '4.0.0',
    },
    'eggs@file:some_file, eggs@file:other_file': {
        'version': '5.0.0',
    },
}

EXPECTED_CONTENT = dedent(
    """\
    # yarn lockfile v1

    foo@^1.0.0:
      version "1.0.0"
      resolved "https://registry.yarnpkg.com/foo/-/foo-1.0.0.tgz"
      dependencies:
        bar "^2.0.0"
      "some number" 1

    bar@^2.0.0:
      version "2.0.0"
      resolved "https://registry.yarnpkg.com/bar/-/bar-2.0.0.tgz"
      "some boolean" true

    "baz@https://example.org/baz.tar.gz":
      version "3.0.0"
      resolved "https://example.org/baz.tar.gz"

    spam@^4.0.0, spam@^4.0.1:
      version "4.0.0"

    "eggs@file:some_file", "eggs@file:other_file":
      version "5.0.0"
    """
)


def test_to_file(tmp_path):
    output_path = tmp_path / "yarn.lock"
    lockfile.Lockfile('1', DATA_TO_DUMP).to_file(output_path)
    assert output_path.read_text() == EXPECTED_CONTENT


def test_to_str():
    content = lockfile.Lockfile('1', DATA_TO_DUMP).to_str()
    assert content == EXPECTED_CONTENT


def test_roundtrip(all_test_files, tmp_path):
    for test_file in all_test_files:
        out_file = tmp_path / os.path.basename(test_file)
        # Check that load -> dump -> load produces expected results
        original = lockfile.Lockfile.from_file(test_file)
        original.to_file(out_file)
        generated = lockfile.Lockfile.from_file(out_file)
        assert original.data == generated.data

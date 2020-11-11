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
import os

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
    pytest.skip("Not implemented")


def test_vx():
    pytest.skip("Not implemented")


@pytest.mark.parametrize('data', [('# comment\n'), ('foo "bar"'), ('foo "bar"\n# comment\n')])
def test_unknown_version(data):
    lock = lockfile.Lockfile.from_str(data)
    assert lock.version == 'unknown'


def test_to_json():
    pytest.skip("Not implemented")

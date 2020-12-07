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


@pytest.fixture
def all_test_files():
    tests_dir = os.path.dirname(__file__)
    test_data_dir = os.path.join(tests_dir, 'data')
    test_data = os.listdir(test_data_dir)
    return [
        os.path.join(test_data_dir, f) for f in test_data
        if os.path.isfile(os.path.join(test_data_dir, f))
    ]

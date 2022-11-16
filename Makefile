# Copyright (C) 2020  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

.PHONY: clean devel check build

check:
	tox

devel:
	pip install -r requirements-dev.txt
	echo 'import setuptools; setuptools.setup()' > setup.py
	pip install -e .
	rm setup.py

clean:
	rm -rf *.egg-info dist build .pytest_cache */__pycache__ pyarn/parsetab.py pyarn/parser.out

# Let's clean up and make sure PLY's parsetab is created
build: clean
	python -c 'from pyarn.lockfile import Lockfile as l; l.from_str("foo bar")'
	python -m build

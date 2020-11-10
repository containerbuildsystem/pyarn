.PHONY: clean devel check build

check:
	flake8 tests pyarn
	pytest -v tests

devel:
	pip install -r requirements-dev.txt
	echo 'import setuptools; setuptools.setup()' > setup.py
	pip install -e .
	rm setup.py

clean:
	rm -rf *.egg-info dist build .pytest_cache */__pycache__

build:
	python -m build

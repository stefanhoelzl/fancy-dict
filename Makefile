.PHONY: default
default: all;

.PHONY: clean
clean:
	rm -rf build dist fancy_dict.egg-info .mpy_cache .pytest_cache docs/_build .htmlcov

.PHONY: tests.unit
tests.unit:
	PYTHONPATH=. pytest tests/unit

.PHONY: tests.coverage
tests.coverage:
	PYTHONPATH=. pytest --cov fancy_dict --cov-report html:.covhtml

.PHONY: tests.lint
tests.lint:
	PYTHONPATH=. pytest tests/lint

.PHONY: tests
tests: tests.unit tests.lint tests.coverage

.PHONY: release.build
release.build:
	python setup.py sdist bdist_wheel

.PHONY: release.upload
release.upload: release.build
	twine upload ${OPTS} dist/*

.PHONY: env.install
env.install:
	python -m pip install -r requirements.txt

.PHONY: docs.build
docs.build:
	sphinx-build -W -b html docs docs/_build

.PHONY: all
all: tests docs.build release.build

.PHONY: ci
ci: all

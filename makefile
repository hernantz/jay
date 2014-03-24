VERSION=$(shell echo `python jay/__init__.py --version`)

build:
	python setup.py sdist && pip install dist/jay-$(VERSION).tar.gz

uninstall:
	pip uninstall -y jay

rebuild: uninstall build

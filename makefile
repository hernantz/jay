build:
	python setup.py sdist && pip install dist/jay-0.1.tar.gz

uninstall:
	pip uninstall -y jay

rebuild: uninstall build

build:
	python setup.py sdist && pip install dist/jay-0.3.tar.gz

uninstall:
	pip uninstall -y jay

requirements:
	pip install -r requirements.txt && pip install -r test-requirements.txt

rebuild: uninstall build
setup: requirements build

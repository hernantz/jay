build:
	python setup.py sdist && pip install dist/jay-0.1.tar.gz

uninstall:
	pip uninstall -y jay

requirements:
	pip install -r requirements.txt

rebuild: uninstall build
setup: requirements build

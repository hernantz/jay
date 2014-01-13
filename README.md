jay
===

A command line tool for quickly jumping around your filesystem. 

## Features
* Fuzzyfind your 100 most recent visited directories. 
* Jump to last visited directory.
* Jump a directory as with cd.
* Quickly access to current directory's siblings by expanding `.`, `..`, `...` 
  into `cwd/`, `cwd/../` and `cwd/../../` respectively.
* Write only the first characters of each dir in the path to get to a 
  nested destination.


## TODO
* jay.rc file with ignores ~/.config/jay/jay.rc DELAYED
* make tests pass
* support zshell and fish
* bash file with f() function to actually perform the jump action
* autocomplete / expand directories


## TEST AND BUILD
To test simply create a virtualenv (virtualenvwrapper is recomended), and run:
`pip install requirements.txt && pip install test-requirements.txt`


After that run the tests with:
`nosetests`


To build the project and do some manual testing run:
`python setup.py sdist && pip install dist/jay-<version>.tar.gz`

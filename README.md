jay
===

A command line tool for quickly jumping around your filesystem. 

## Features
* Fuzzyfind your 100 most recent visited directories. 
* Jump to last visited directory with just j.
* Jump a directory as with cd.
* Quickly access to current directory's siblings by expanding `.`, `..`, `...` 
  into `cwd/`, `cwd/../` and `cwd/../../` respectively.
* Write only the first characters of each dir in the path to get to a 
  nested destination.
* `j .` => goes to cwd and not into cwd/.exampledir
* `j ..` => goes to cwd/../ and not into cwd/..exampledir
* `j ...` => goes to cwd/../../ and not into cwd/...exampledir
* be case insensitive, but case is important (?)
* fuzzy relative navigation `j .` dir should go to cwd/exampledir


## TODO
* jay.rc file with ignores ~/.config/jay/jay.rc DELAYED
* make tests pass (ALWAYS)
* support zshell and fish
* bash file with f() function to actually perform the jump action
* autocomplete / expand directories


## CONTRIBUTING CODE
* Open an issue to discuss the feature/bug you want to work on
* Fork the repo and create a new branch
* Submit a pull request against the `develop` branch


## TEST AND BUILD
To test simply create a virtualenv (virtualenvwrapper is recomended), and inside of it run:
`make requirements`


After that run the tests with:
`nosetests`


To run a single test run
`nosetests path/to/tests.py:test_function_name`


To build the project and do some manual testing, inside a virtualenv run:
`make build` or `make rebuild`


Then to get bash goodies (j function and autocompletion) source the output of:
`jay --setup-bash`

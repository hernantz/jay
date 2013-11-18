jay
===

A command line tool for quickly jumping around your filesystem. 

## Features
* Fuzzyfind your 100 most recent visited directories. 
* Jump to last visited directory.
* Quickly access to current directory's siblings by expanding `.`, `..`, `...` 
  into `cwd/`, `cwd/../` and `cwd/../../` respectively.
* Write only the first characters of each dir in the path to get to a 
  nested destination.


## TODO
* build and mantain index ~/.data/jay/index DONE
* visit directory exact match DONE
* expand . into cwd DONE
* expand .. into cwd/../ DONE
* expand ... into cwd/../../ DONE
* jump to last visited dir with j - DONE
* jay.rc file para ignores ~/.config/jay/jay.rc DELAYED
* tests with cram
* distribute
* autocomplete / expand directories

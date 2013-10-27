"""
Usage: my_program.py [-hso FILE] [--quiet | --verbose] [INPUT ...]

-h --help       show this
-s --sorted     sorted output
-o FILE         specify output file [default: ./test.txt]
-x --build-idx  build/rebuild directory index
--quiet         print less text
--verbose       print more text
--version       print current version
"""""

"""
TODO
build and mantain index ~/.data/jay/index
jay.rc file para ignores ~/.config/jay/jay.rc
autocomplete / expand
visit directory exact match DONE
expand . into cwd DONE
expand .. into cwd/../ DONE
expand ... into cwd/../../ DONE
jump to last visited dir with j
tests
deploy
"""


__version__ = '0.1'
import os
from docopt import docopt
from fuzzywuzzy import process




def relative_of_cwd(term):
    """checks if term matches a relative directory of our cwd"""
    # if term is ... convert it to cwd + ../ + ../
    term = os.path.join('..', '..') if term == '...' else term

    relative_of_cwd = os.path.join(os.getcwd(), term)
    if os.path.isdir(relative_of_cwd):
        return os.path.abspath(relative_of_cwd)
    return None


def walkdir(rootdir, terms):
    if len(terms) == 0:
        return rootdir

    term = terms.pop()
    matched_dir = ''
    for d in os.listdir(rootdir):
        if d.startswith(term):
            matched_dir = d
            break
    else:
        return None
    fulldir = os.path.join(rootdir, matched_dir)
    return walkdir(fulldir, terms)


def main(args):
    search_terms = args['INPUT']

    # if len(terms) is 0:
    #    jump to previous directory
    if not len(search_terms):
        print(os.path.expanduser('~'))
        exit(0)


    first_term = search_terms[0]  # first search term
    rel_directory = relative_of_cwd(first_term)

    # if len(search_terms) is > 1:
    #   if first arg is a relative dir, use it as rootdir and then
    #   recursively search for best match with starting chars of each arg
    if len(search_terms) > 1:
        args['INPUT'].reverse()
        rootdir = rel_directory if rel_directory else '/'
        if rel_directory:
            args['INPUT'].pop()  # becouse rel_directory is our rootdir now
        result = walkdir(rootdir, terms=args['INPUT'])
        if result:
            print(result)
            exit(0)
        exit(1)  # else we didn't find anything


    # if len(terms) is 1:
    #   if is dir? cd to dir
    if rel_directory:
        print(rel_directory)
        exit(0)

    # if len(input) is 1:
    #   fuzzy search index, cd to dir
    with open('index') as data:
        directories = sorted(data.read().splitlines())
    result = process.extractOne(first_term, directories)
    if result:
        directory, score = result
        print(directory)
        exit(0)

    exit(1)  # else we didn't find anything

if __name__ == '__main__':
    args = docopt(__doc__, argv=None, help=True,
                  options_first=False, version=__version__)
    main(args)

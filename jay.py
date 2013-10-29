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
jump to last visited dir with j - DONE
tests
deploy
"""


__version__ = '0.1'
import os
from docopt import docopt
from fuzzywuzzy import process


RECENT_IDX_DIR =  '/home/hernantz/devel/jay/recent'
IDX_DIR = '/home/hernantz/devel/jay/index'
DIR_IDX_MAX_SIZE = 100


class JayDirectoryIndex(object):
    """Singleton of directories index"""

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(JayDirectoryIndex, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        with open(IDX_DIR, 'r') as f:
            data = f.read().splitlines()
            self.indexed_directories = set(sorted(data))

    def fuzzyfind(self, term):
        result = process.extractOne(term, self.indexed_directories)
        if result:
            directory, score = result
            return directory
        return None

    def update(self, d):
        """Write the directory to the index file"""
        self.indexed_directories.add(d)
        with open(IDX_DIR, 'w') as f:
            lines = ['{}\n'.format(d) for d in self.indexed_directories]
            f.writelines(lines)


def recent_dir():
    """Get the first line of the RECENT_DIR_IDX file"""
    with open(RECENT_IDX_DIR, 'r') as f:
        d = f.read().splitlines()
    try:
        return d[0]
    except IndexError:
        return ''


def update_recent_dir():
    """Write the cwd to the RECENT_DIR_IDX file"""
    with open(RECENT_IDX_DIR, 'w') as f:
        f.writelines([os.getcwd()])


def dispatch(d):
    """Saves cwd, updates the index and prints the matched directory"""
    update_recent_dir()
    JayDirectoryIndex().update(d)
    print(d)
    exit(0)


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
    #    jump to $HOME
    if not len(search_terms):
        dispatch(os.path.expanduser('~'))


    first_term = search_terms[0]  # first search term

    # '-' means jump to previous directory
    # otherwise check if first_term is a relative dir of cwd
    rel_directory = recent_dir() if first_term == '-' else relative_of_cwd(first_term)


    # if len(search_terms) is > 1:
    #   if first arg is a relative dir, use it as rootdir and then
    #   recursively search for best match with starting chars of each arg
    if len(search_terms) > 1:
        search_terms.reverse()
        rootdir = rel_directory if rel_directory else '/'
        if rel_directory:
            search_terms.pop()  # becouse rel_directory is our rootdir now
        result = walkdir(rootdir, terms=search_terms)
        if result:
            dispatch(result)
        exit(1)  # else we didn't find anything


    # if len(terms) is 1:
    #   if is dir? cd to dir
    if rel_directory:
        dispatch(rel_directory)

    # if len(input) is 1:
    #   fuzzy search index, cd to dir
    directory = JayDirectoryIndex().fuzzyfind(first_term)
    if directory:
        dispatch(directory)

    exit(1)  # else we didn't find anything


if __name__ == '__main__':
    args = docopt(__doc__, argv=None, help=True,
                  options_first=False, version=__version__)
    main(args)

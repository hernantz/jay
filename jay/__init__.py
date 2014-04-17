from __future__ import unicode_literals
import os
import sys
import io
from os.path import join
from docopt import docopt
from fuzzywuzzy import process
from xdg import BaseDirectory
from time import time
import csv


if sys.version_info.major < 3:
    import unicodecsv as csv


__doc__ = """
Usage:
    jay [-h] [--setup-bash | --version] [INPUT ...]
    jay --autocomplete <current-position> <params>...

-h --help       show this
--setup-bash    setup `j` function and autocomplete for bash
--version       print current version
--autocomplete  provides autocompletion instead of just one matching dir
"""


__version__ = '0.1'

JAY_XDG_DATA_HOME = BaseDirectory.save_data_path('jay')
RECENT_IDX_FILENAME = join(JAY_XDG_DATA_HOME, 'recent')
IDX_FILENAME = join(JAY_XDG_DATA_HOME, 'index')  # index filename
IDX_MAX_SIZE = 100  # max number of entries in the index
READ_MODE = 'rb' if sys.version_info.major < 3 else 'r'
WRITE_MODE = 'wb' if sys.version_info.major < 3 else 'w'


class Jay(object):
    """Singleton of directories index"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Jay, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, idx_filename=IDX_FILENAME,
                 idx_max_size=IDX_MAX_SIZE, recent_idx_filename=RECENT_IDX_FILENAME):
        self.idx = idx_filename
        self.idx_max_size = idx_max_size
        self.recent_idx = recent_idx_filename
        self.idx_rows = {}

        # create the idx file if does not exist
        if not os.path.isfile(self.idx):
            try:
                with io.open(self.idx, 'w') as f:
                    pass
            except:
                raise Exception("jay: an error ocurred while creating the index {}.".format(self.idx))

        try:
            with io.open(self.idx, 'r') as f:
                # get each row from index,
                # where each csv row is [dir, access_timestamp]
                self.idx_rows = {d: ts for d, ts in csv.reader(f)}
        except:
            raise Exception("jay: an error ocurred while opening the index {}.".format(self.idx))

    def fuzzyfind(self, term):
        result = process.extractOne(term, sorted(self.idx_rows.keys()))
        if result:
            directory, score = result
            return directory
        return None

    def update(self, d):
        """Write the directory to the index file"""
        self.idx_rows.update({d: str(time())})
        self.dump()

    def delete(self, d):
        """Remove the directory from the index file"""
        self.idx_rows.pop(d, None)
        self.dump()

    def dump(self):
        """Dump the dirs to the index file"""
        with io.open(self.idx, WRITE_MODE) as f:
            # save the most recent dirs only
            rows = [tup for tup in self.idx_rows.items()]
            rows = sorted(rows, key=lambda x: x[1], reverse=True)
            csv.writer(f).writerows(rows[:self.idx_max_size])

    @property
    def recent_dir(self):
        """Get the first line of the RECENT_DIR_IDX file"""
        try:
            with io.open(self.recent_idx, 'r') as f:
                d = f.read().splitlines()
        except IOError:
            return ''
        else:
            try:
                return d[0]
            except IndexError:
                return ''

    def update_recent_dir(self):
        """Write the cwd to the RECENT_DIR_IDX file"""
        try:
            with io.open(self.recent_idx, WRITE_MODE) as f:
                f.writelines([os.getcwd()])
        except:
            raise Exception("jay: an error ocurred while opening the recent index {}.".format(self.recent_idx))


def dispatch(d):
    """Try to saves cwd, updates the index and print
       the matched directory"""
    j = Jay()
    if not os.path.isdir(d):
        try:
            j.delete(d)
        except Exception as e:
            out(e)
        else:
            out("jay: directory {} not found.".format(d))
        finally:
            return 1
    try:
        j.update_recent_dir()
        j.update(d)
    except Exception as e:
        out(e)
        return 1
    else:
        out(d)
        return 0


def relative_of_cwd(term):
    """checks if term matches a relative directory of our cwd"""
    # if term is ... convert it to cwd + ../ + ../
    term = join('..', '..') if term == '...' else term

    rel_of_cwd = join(os.getcwd(), term)
    if os.path.isdir(rel_of_cwd):
        return os.path.abspath(rel_of_cwd)
    return None


def walkdir(rootdir, terms):
    """
    Recursively searches for child directories of the rootdir
    `terms` is a list that matches fuzzyly from the child directory name
    for example, if user typed `jay /root dir1 dir2` then the lookup would be:
    1) walkdir('/root', terms=['dir2', 'dir1']) --> walkdir('/root/dir1', terms=['dir2'])
    2) walkdir('/root/dir1', terms=['dir2']) --> walkdir('/root/dir1/dir2', terms=[])
    3) walkdir('/root/dir1/dir2', terms=[]) --> '/root/dir1/dir2'
    """
    if not len(terms):
        return rootdir

    term = terms.pop()
    matched_dir = ''
    match = process.extractOne(term, listdir(rootdir))
    if match:
        matched_dir, score = match
    fulldir = join(rootdir, matched_dir)
    return walkdir(fulldir, terms)


def listdir(path):
    """Lists directories only"""
    directories = []
    for d in os.listdir(path):
        if not os.path.isdir(os.path.join(path, d)):
            continue
        directories.append(d)
    return sorted(directories)


def autocomplete(params, current_position):
    out(current_position)


def run(args):

    if args['--setup-bash']:
        setup_bash()
        return 0

    if args['--autocomplete']:
        return autocomplete(params=args['<params>'],
                            current_position=args['<current-position>'])

    search_terms = args['INPUT']

    # if len(terms) is 0 jump to previous dir
    if not len(search_terms):
        return dispatch(Jay().recent_dir)

    first_term = search_terms[0]  # first search term

    # '-' means jump to previous directory
    # otherwise check if first_term is a relative dir of cwd
    rel_directory = Jay().recent_dir if first_term == '-' else relative_of_cwd(first_term)

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
            return dispatch(result)
        return 1  # else we didn't find anything

    # len(terms) is 1, if rel_directory is a dir, cd to it
    if rel_directory:
        return dispatch(rel_directory)

    # len(input) is 1, fuzzy search index with the term, cd to matched dir
    directory = Jay().fuzzyfind(first_term)
    if directory:
        return dispatch(directory)

    return 1  # else we didn't find anything


def setup_bash():
    print(os.path.join(os.path.dirname(__file__), 'jay.bash'))
    print(os.path.join(os.path.dirname(__file__), 'jay-autocomplete.bash'))


def out(d):
    """Just output the result.
       Helps mocking for tests, and maybe in the future
       this could be used to provide other forms of output"""
    print(d)


def main():
    args = docopt(__doc__, argv=None, help=True,
                  options_first=False, version=__version__)
    return run(args)


if __name__ == '__main__':
    sys.exit(main())

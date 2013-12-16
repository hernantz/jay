import os
import sys
sys.path.insert(0, os.path.abspath('..'))
from jay import Jay
from nose.tools import with_setup


TEST_DIR = os.path.join('test', os.path.abspath(os.path.dirname(__file__)))
TEST_RECENT_IDX_FILENAME = os.path.join(TEST_DIR, 'recent')
TEST_IDX_FILENAME = os.path.join(TEST_DIR, 'index')
TEST_IDX_MAX_SIZE = 100


def teardown_idx():
    os.remove(TEST_IDX_FILENAME)


@with_setup(teardown=teardown_idx)
def test_idx_is_created():
    """Directory index should be created if it
       doesn't exist"""
    assert not os.path.isfile(TEST_IDX_FILENAME)
    Jay(idx_filename=TEST_IDX_FILENAME)
    assert os.path.isfile(TEST_IDX_FILENAME)


@with_setup(teardown=teardown_idx)
def test_singleton():
    """Jay class should be a singleton"""
    j1 = Jay(idx_filename=TEST_IDX_FILENAME)
    j2 = Jay(idx_filename=TEST_IDX_FILENAME)
    assert j1 is j2

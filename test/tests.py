import os
import sys
import mock
import jay
sys.path.insert(0, os.path.abspath('..'))
from jay import Jay
from nose.tools import with_setup


TEST_DIR = os.path.join('test', os.path.abspath(os.path.dirname(__file__)))
TEST_RECENT_IDX_FILENAME = os.path.join(TEST_DIR, 'recent')
TEST_IDX_FILENAME = os.path.join(TEST_DIR, 'index')
TEST_IDX_MAX_SIZE = 3


def setup_idx():
    with open(TEST_IDX_FILENAME, 'w') as f:
        f.write('/tmp/dir1,1387159989.41\n')
        f.write('/home/dir2,1387158735.64')


def teardown_idx():
    os.remove(TEST_IDX_FILENAME)


def _update(jay_instance, directory, update_time):
    with mock.patch.object(jay, 'time', return_value=update_time):
        jay_instance.update(directory)


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


@with_setup(teardown=teardown_idx)
def test_empty_idx_content_is_loaded_from_file():
    """An empty idx file should be loaded with no entries"""
    expected_rows = {}
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    assert j.idx_rows == expected_rows


@with_setup(setup=setup_idx, teardown=teardown_idx)
def test_idx_content_is_loaded_from_file():
    """Idx file entries should be loaded as a dict"""
    expected_rows = {'/tmp/dir1': '1387159989.41',
                     '/home/dir2': '1387158735.64'}
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    assert j.idx_rows == expected_rows


@with_setup(teardown=teardown_idx)
def test_update_with_new_directory():
    """Jay.update should add the entry time for a new directory"""
    assert not os.path.isfile(TEST_IDX_FILENAME)
    d = '/test/dir'
    update_time = '1387159989.41'
    j = Jay(idx_filename=TEST_IDX_FILENAME)

    _update(j, d, update_time)
    assert j.idx_rows == {d: update_time}


@with_setup(teardown=teardown_idx)
def test_update_with_existing_directory():
    """Jay.update should update the entry time of an existing entry"""
    assert not os.path.isfile(TEST_IDX_FILENAME)
    d = '/test/dir'
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    future_time = '2222222222.41'

    _update(j, d, update_time='1387159989.41')
    _update(j, d, future_time)
    assert j.idx_rows == {d: future_time}


@with_setup(teardown=teardown_idx)
def test_delete_with_existing_directory():
    """Jay.delete should delete an existing entry"""
    assert not os.path.isfile(TEST_IDX_FILENAME)
    d = '/test/dir'
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    update_time = '1387159989.41'
    _update(j, d, update_time)

    j.delete(d)
    assert j.idx_rows == {}


@with_setup(teardown=teardown_idx)
def test_delete_with_non_existing_directory():
    """Jay.delete should not break when deleting
       an non existing entry"""
    assert not os.path.isfile(TEST_IDX_FILENAME)
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    j.delete('/non/existent/dir')
    assert j.idx_rows == {}


@with_setup(teardown=teardown_idx)
def test_updates_are_persisted():
    """Idx updates should be persisted"""
    d = '/test/dir'
    update_time = '1387159989.41'
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    _update(j, d, update_time)
    expected_output = '{0},{1}'.format(d, update_time)
    assert open(TEST_IDX_FILENAME).read().strip() == expected_output


@with_setup(setup=setup_idx, teardown=teardown_idx)
def test_deletions_are_persisted():
    """Idx deletions should be persisted"""
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    j.delete('/tmp/dir1')  # delete an existent entry
    expected_output = '/home/dir2,1387158735.64' # the other entry
    assert open(TEST_IDX_FILENAME).read().strip() == expected_output


@with_setup(teardown=teardown_idx)
def test_dump():
    """Dump method should persist idx_rows"""
    d = '/test/dir'
    update_time = '1387159989.41'
    expected_output = '{0},{1}'.format(d, update_time)

    j = Jay(idx_filename=TEST_IDX_FILENAME)
    j.idx_rows = {d: update_time}
    j.dump()
    assert open(TEST_IDX_FILENAME).read().strip() == expected_output

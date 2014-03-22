from __future__ import unicode_literals
import os
import sys
import mock
import jay
import io
import shutil
from docopt import docopt
sys.path.insert(0, os.path.abspath('..'))
from jay import Jay, run, __doc__, relative_of_cwd, walkdir, listdir
from nose.tools import with_setup


TEST_DIR = os.path.join('tests', os.path.abspath(os.path.dirname(__file__)), 'testdirs')
TEST_RECENT_IDX_FILENAME = os.path.join(TEST_DIR, 'recent')
TEST_IDX_FILENAME = os.path.join(TEST_DIR, 'index')
TEST_IDX_MAX_SIZE = 2


def setup_idx():
    mkdir('')
    with io.open(TEST_IDX_FILENAME, 'w') as f:
        f.write('/tmp/dir1,1387159989.41\n')
        f.write('/home/dir2,1387158735.64')


def teardown_dirs():
    shutil.rmtree(TEST_DIR)


def mkdir(*args):
    """Recursively create dirs"""
    for d in args:
        rel_d = os.path.join(TEST_DIR, d)
        os.makedirs(rel_d)


def touch(*args):
    """Recursively create files"""
    for f in args:
        rel_f = os.path.join(TEST_DIR, f)
        io.open(rel_f, 'w')


def teardown_both_idx():
    teardown_dirs()


def _update(jay_instance, directory, update_time):
    with mock.patch.object(jay, 'time', return_value=update_time):
        jay_instance.update(directory)


@with_setup(teardown=teardown_both_idx)
def test_idx_is_created():
    """Directory index should be created if it
       doesn't exist"""
    mkdir('')
    assert not os.path.isfile(TEST_IDX_FILENAME)
    Jay(idx_filename=TEST_IDX_FILENAME)
    assert os.path.isfile(TEST_IDX_FILENAME)


@with_setup(teardown=teardown_both_idx)
def test_singleton():
    """Jay class should be a singleton"""
    mkdir('')
    j1 = Jay(idx_filename=TEST_IDX_FILENAME)
    j2 = Jay(idx_filename=TEST_IDX_FILENAME)
    assert j1 is j2


@with_setup(teardown=teardown_both_idx)
def test_empty_idx_content_is_loaded_from_file():
    """An empty idx file should be loaded with no entries"""
    expected_rows = {}
    mkdir('')
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    assert j.idx_rows == expected_rows


@with_setup(setup=setup_idx, teardown=teardown_both_idx)
def test_idx_content_is_loaded_from_file():
    """Idx file entries should be loaded as a dict"""
    expected_rows = {'/tmp/dir1': '1387159989.41',
                     '/home/dir2': '1387158735.64'}
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    assert j.idx_rows == expected_rows


@with_setup(teardown=teardown_both_idx)
def test_dump_max_num_entries():
    """Dump method should persist not more than the max idx rows allowed"""
    assert TEST_IDX_MAX_SIZE == 2

    d1 = '/test/dir1'
    d2 = '/test/dir2'
    d3 = '/test/dir3'
    update_time1 = '1100000000.00'
    update_time2 = '1200000000.00'
    update_time3 = '1300000000.00'
    expected_output = ['{0},{1}\n'.format(d3, update_time3),
                       '{0},{1}\n'.format(d2, update_time2)]

    mkdir('')
    j = Jay(idx_filename=TEST_IDX_FILENAME,
            idx_max_size=TEST_IDX_MAX_SIZE)
    j.idx_rows = {d1: update_time1, d2: update_time2, d3: update_time3}
    j.dump()
    assert io.open(TEST_IDX_FILENAME).readlines() == expected_output


@with_setup(teardown=teardown_both_idx)
def test_update_with_new_directory():
    """Jay.update should add the entry time for a new directory"""
    mkdir('')
    assert not os.path.isfile(TEST_IDX_FILENAME)
    d = '/test/dir'
    update_time = '1387159989.41'
    j = Jay(idx_filename=TEST_IDX_FILENAME)

    _update(j, d, update_time)
    assert j.idx_rows == {d: update_time}


@with_setup(teardown=teardown_both_idx)
def test_update_with_existing_directory():
    """Jay.update should update the entry time of an existing entry"""
    mkdir('')
    assert not os.path.isfile(TEST_IDX_FILENAME)
    d = '/test/dir'
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    future_time = '2222222222.41'

    _update(j, d, update_time='1387159989.41')
    _update(j, d, future_time)
    assert j.idx_rows == {d: future_time}


@with_setup(teardown=teardown_both_idx)
def test_delete_with_existing_directory():
    """Jay.delete should delete an existing entry"""
    mkdir('')
    assert not os.path.isfile(TEST_IDX_FILENAME)
    d = '/test/dir'
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    update_time = '1387159989.41'
    _update(j, d, update_time)

    j.delete(d)
    assert j.idx_rows == {}


@with_setup(teardown=teardown_both_idx)
def test_delete_with_non_existing_directory():
    """Jay.delete should not break when deleting
       an non existing entry"""
    mkdir('')
    assert not os.path.isfile(TEST_IDX_FILENAME)
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    j.delete('/non/existent/dir')
    assert j.idx_rows == {}


@with_setup(teardown=teardown_both_idx)
def test_updates_are_persisted():
    """Idx updates should be persisted"""
    mkdir('')
    d = '/test/dir'
    update_time = '1387159989.41'
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    _update(j, d, update_time)
    expected_output = '{0},{1}'.format(d, update_time)
    assert io.open(TEST_IDX_FILENAME).read().strip() == expected_output


@with_setup(setup=setup_idx, teardown=teardown_both_idx)
def test_deletions_are_persisted():
    """Idx deletions should be persisted"""
    j = Jay(idx_filename=TEST_IDX_FILENAME)
    j.delete('/tmp/dir1')  # delete an existent entry
    expected_output = '/home/dir2,1387158735.64' # the other entry
    assert io.open(TEST_IDX_FILENAME).read().strip() == expected_output


@with_setup(teardown=teardown_both_idx)
def test_dump():
    """Dump method should persist idx_rows"""
    mkdir('')
    d = '/test/dir'
    update_time = '1387159989.41'
    expected_output = '{0},{1}'.format(d, update_time)

    j = Jay(idx_filename=TEST_IDX_FILENAME,
            recent_idx_filename=TEST_RECENT_IDX_FILENAME)
    j.idx_rows = {d: update_time}
    j.dump()
    assert io.open(TEST_IDX_FILENAME).read().strip() == expected_output


@with_setup(teardown=teardown_both_idx)
def test_recent_dir():
    """Jay.recent_dir should return the first line
       in recent idx file"""
    mkdir('')
    with io.open(TEST_RECENT_IDX_FILENAME, 'w') as f:
        f.write('/dumb/dir1\n')
        f.write('/dumb/dir2')

    j = Jay(idx_filename=TEST_IDX_FILENAME,
            recent_idx_filename=TEST_RECENT_IDX_FILENAME)
    assert j.recent_dir == '/dumb/dir1'


@with_setup(teardown=teardown_both_idx)
def test_nonexistant_recent_dir():
    """Jay.recent_dir should return an empty string
       if the recent idx file is empty"""
    mkdir('')
    assert not os.path.isfile(TEST_RECENT_IDX_FILENAME)
    j = Jay(idx_filename=TEST_IDX_FILENAME,
            recent_idx_filename=TEST_RECENT_IDX_FILENAME)
    assert j.recent_dir == ''


@with_setup(teardown=teardown_both_idx)
def test_empty_recent_dir():
    """jay.recent_dir should return an empty string
       if the recent idx file is empty"""
    assert not os.path.isfile(TEST_RECENT_IDX_FILENAME)

    mkdir('')
    with io.open(TEST_RECENT_IDX_FILENAME, 'w'):
        pass

    j = Jay(idx_filename=TEST_IDX_FILENAME,
            recent_idx_filename=TEST_RECENT_IDX_FILENAME)
    assert j.recent_dir == ''


def test_run_without_args():
    """Calling jay without args should yield the users home dir"""
    args = docopt(__doc__, argv=[])
    fake_out = mock.Mock()
    with mock.patch('jay.out', fake_out):
        return_code = run(args)
    fake_out.assert_called_once_with("{}".format(os.path.expanduser('~')))
    assert return_code == 0


@with_setup(teardown=teardown_dirs)
def test_relative_of_cwd_with_one_dot():
    """Calling jay with `.` should be expanded to cwd"""
    mkdir('')
    with mock.patch.object(os, 'getcwd', return_value=TEST_DIR):
        result = relative_of_cwd('.')
    assert TEST_DIR == result


@with_setup(teardown=teardown_dirs)
def test_relative_of_unexistant_cwd_with_one_dot():
    """Calling jay with `.` on a non existant dir should yield None"""
    mkdir('')
    fake_dir = os.path.join(TEST_DIR, 'fake_dir')
    assert not os.path.isdir(fake_dir)

    with mock.patch.object(os, 'getcwd', return_value=fake_dir):
        result = relative_of_cwd('.')
    assert result is None


@with_setup(teardown=teardown_dirs)
def test_relative_of_cwd_with_one_dot_and_one_dotted_child():
    """Calling jay with `. with a .dir should prioratize cwd over
       the dotted dirname"""
    mkdir('.dir')
    with mock.patch.object(os, 'getcwd', return_value=TEST_DIR):
        result = relative_of_cwd('.')
    assert result == TEST_DIR


@with_setup(teardown=teardown_dirs)
def test_relative_of_cwd_with_two_dots_and_two_dotted_child():
    """Calling jay with `.. with a ..dir should prioratize ../cwd over
       the dotted dirname"""
    mkdir('dir/..dir')
    cwd = os.path.join(TEST_DIR, 'dir')  # im in TEST_DIR/dir/
    with mock.patch.object(os, 'getcwd', return_value=cwd):
        result = relative_of_cwd('..')
    assert result == TEST_DIR


@with_setup(teardown=teardown_dirs)
def test_relative_of_cwd_with_three_dots_and_three_dotted_child():
    """Calling jay with `... with a ...dir should prioratize ../../cwd over
       the dotted dirname"""
    mkdir('dir/dir2/...dir')
    cwd = os.path.join(TEST_DIR, 'dir', 'dir2')  # im in TEST_DIR/dir/dir2/
    with mock.patch.object(os, 'getcwd', return_value=cwd):
        result = relative_of_cwd('...')
    assert result == TEST_DIR


@with_setup(teardown=teardown_dirs)
def test_relative_of_cwd_with_two_dots():
    """Calling jay with `..` should be expanded to cwd/../"""
    mkdir('dir1/dir2')
    one_level_deep_dir = os.path.join(TEST_DIR, 'dir1')
    two_level_deep_dir = os.path.join(TEST_DIR, 'dir1', 'dir2')
    with mock.patch.object(os, 'getcwd', return_value=two_level_deep_dir):
        result = relative_of_cwd('..')
    assert one_level_deep_dir == result


@with_setup(teardown=teardown_dirs)
def test_nonexistant_relative_of_cwd_with_two_dots():
    """Calling jay with `..` should return None if cwd/../ doesn't exists"""
    mkdir('')  # just rootdir
    fake_dir = os.path.join(TEST_DIR, 'fake_dir')
    assert not os.path.isdir(fake_dir)

    two_level_deep_dir = os.path.join(TEST_DIR, 'fake_dir', 'dir2')
    with mock.patch.object(os, 'getcwd', return_value=two_level_deep_dir):
        result = relative_of_cwd('..')
    assert result is None


@with_setup(teardown=teardown_dirs)
def test_relative_of_cwd_with_three_dots():
    """Calling jay with `...` should be expanded to cwd/.../.../"""
    mkdir('dir1/dir2')
    two_level_deep_dir = os.path.join(TEST_DIR, 'dir1', 'dir2')
    with mock.patch.object(os, 'getcwd', return_value=two_level_deep_dir):
        result = relative_of_cwd('...')
    assert TEST_DIR == result


@with_setup(teardown=teardown_dirs)
def test_nonexistant_relative_of_cwd_with_three_dots():
    """Calling jay with `...` should None if cwd/.../.../ doesn't exists"""
    mkdir('')  # just rootdir
    fake_dir = os.path.join(TEST_DIR, 'fake_dir')
    assert not os.path.isdir(fake_dir)

    two_level_deep_dir = os.path.join(fake_dir, 'dir1', 'dir2')
    with mock.patch.object(os, 'getcwd', return_value=two_level_deep_dir):
        result = relative_of_cwd('...')
    assert result is None


@with_setup(teardown=teardown_dirs)
def test_listdir_returns_dirs_only():
    """listdir function should returns child directories only"""
    mkdir('dir')
    touch('file')
    assert ['dir'] == listdir(TEST_DIR)


@with_setup(teardown=teardown_dirs)
def test_listdir_returns_a_sorted_list_of_child_dirs():
    """listdir function should return a sorted list of child directories"""
    mkdir('dir1', 'dir2')
    assert ['dir1', 'dir2'] == listdir(TEST_DIR)


@with_setup(teardown=teardown_dirs)
def test_walkdir_without_terms():
    """Calling walkdir without terms should return the rootdir"""
    mkdir('')  # just rootdir
    assert TEST_DIR == walkdir(TEST_DIR, terms=[])


@with_setup(teardown=teardown_dirs)
def test_walkdir_without_one_existing_dir_returns_rootdir():
    """Calling walkdir without one existing dir as terms should returns rootdir"""
    mkdir('')  # just rootdir
    assert not os.path.isdir(os.path.join(TEST_DIR, 'fake_dir'))
    expected_result = os.path.join(TEST_DIR, '')
    assert expected_result == walkdir(TEST_DIR, terms=['fake_dir'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_without_existings_dirs_returns_rootdir():
    """Calling walkdir without one existing dir as terms should returns rootdir"""
    mkdir('')  # just rootdir
    assert not os.path.isdir(os.path.join(TEST_DIR, 'fake_dir1', 'fake_dir2'))
    expected_result = os.path.join(TEST_DIR, '')
    assert expected_result == walkdir(TEST_DIR, terms=['fake_dir2', 'fake_dir1'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_with_fuzzy_names():
    """Walkdir should support fuzzy finding for child dirs"""
    mkdir('dir1/filedir', 'dir1/filedir2')
    expected_result = os.path.join(TEST_DIR, 'dir1', 'filedir')
    assert expected_result == walkdir(TEST_DIR, terms=['dir', 'dir'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_with_fuzzy_names_in_different_parts_of_the_dirname():
    """Walkdir should prioratize matching at the begining of the dirname when
       fuzzy finding for child dirs"""
    mkdir('dir1/filedir', 'dir1/dir', 'dir1/dir1')
    expected_result = os.path.join(TEST_DIR, 'dir1', 'dir')
    assert expected_result == walkdir(TEST_DIR, terms=['dir', 'dir'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_with_one_existing_dir():
    """Calling walkdir with one existing dir as terms should return that dir"""
    mkdir('dir1')
    expected_result = os.path.join(TEST_DIR, 'dir1')
    assert expected_result == walkdir(TEST_DIR, terms=['dir1'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_without_two_existing_dirs_and_one_fake_subdir():
    """Walkdir should return the path until the last dir that exists"""
    mkdir('dir1/dir2')
    assert not os.path.isdir(os.path.join(TEST_DIR, 'dir1', 'dir2', 'fake_dir'))
    expected_result = os.path.join(TEST_DIR, 'dir1', 'dir2', '')
    assert expected_result == walkdir(TEST_DIR, terms=['fake_dir', 'dir2', 'dir1'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_with_a_filename():
    """Walkdir should return the path until the last dir that exists"""
    mkdir('dir1')
    touch('dir1/file1')
    expected_result = os.path.join(TEST_DIR, 'dir1', '')
    assert expected_result == walkdir(TEST_DIR, terms=['file1', 'dir1'])


@with_setup(teardown=teardown_dirs)
def test_walkdir_with_ambiguous_terms():
    """Walkdir should return the path for the first dir that matches the term"""
    mkdir('dir1/filedir', 'dir1/filedir2')
    touch('dir1/file1')  # caution a file!
    expected_result = os.path.join(TEST_DIR, 'dir1', 'filedir')
    assert expected_result == walkdir(TEST_DIR, terms=['file', 'dir1'])

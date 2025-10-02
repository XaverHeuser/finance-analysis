"""Tests for local storage utility functions."""

import infrastructure.local_storage as local_storage


def test_get_all_acc_states_from_local_storage(tmp_path):
    """It should return only files containing 'Kontoauszug'."""
    # Create some files
    file1 = tmp_path / 'Kontoauszug_2025_01.pdf'
    file1.write_text('dummy content')

    file2 = tmp_path / 'Kontoauszug_2025_02.pdf'
    file2.write_text('dummy content')

    file3 = tmp_path / 'otherfile.txt'
    file3.write_text('dummy content')

    # Create a directory to ensure it's ignored
    dir1 = tmp_path / 'Kontoauszug_folder'
    dir1.mkdir()

    result = local_storage.get_all_acc_states_from_local_storage(tmp_path)
    result_names = [f.name for f in result]

    assert file1.name in result_names
    assert file2.name in result_names
    assert 'otherfile.txt' not in result_names
    assert 'Kontoauszug_folder' not in result_names

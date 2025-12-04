import pytest
from common_utils.io_handler import file as filemod


def test_save_and_read_text(tmp_path):
    # create a path under the tmp_path (tmp_path should be under the user's home dir in typical pytest runs)
    target = tmp_path / "tests_subdir" / "hello.txt"
    # ensure parent doesn't exist yet
    assert not target.parent.exists()

    # write and read
    filemod.save_to_file("hello world", str(target))
    content = filemod.read_file(str(target))
    assert content == "hello world"


def test_remove_dir_raises_for_file(tmp_path):
    f = tmp_path / "a_file.txt"
    f.write_text("x")
    with pytest.raises(NotADirectoryError):
        filemod.remove_dir(str(f))

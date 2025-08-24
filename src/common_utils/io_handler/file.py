from common_utils import __name__ as pkg_name
import importlib.resources as resources
from pathlib import Path
import json
import yaml
import tomllib
import PyPDF2


_ALLOWED_FILE_READER_EXTENSION = {
    # specific read func
    ".yaml": yaml.safe_load,
    ".json": json.load,
    ".toml": tomllib.load,
    ".pdf": PyPDF2.PdfFileReader,
    # these just get opened with the standard .read()
    ".csv": None,
    ".txt": None,
    ".sql": None,
}


def prepare_file_path(file_path):
    """
    If the directory (and it's subdirs) doesn't exist then it will get created.
    Note that this doesn't direct create the file and actually the absolute file path

    Also it the saved data to live somewhere in C drive. This behaviour might
    need to be changed in the future tho...
    """
    # get absolute path
    save_path = Path(file_path).resolve()
    parent_dir = save_path.parent

    # expects file to be "C:\Users\name"
    root_path = Path.home().resolve()

    if not parent_dir.is_relative_to(root_path):
        raise ValueError(f"{save_path} path should start with {root_path}")

    # create the dir and any subdirs that doesn't exist
    parent_dir.mkdir(parents=True, exist_ok=True)

    return save_path


def read_file(file_path, build_parent_dir=False, **kwargs):
    file_path = prepare_file_path(file_path) if build_parent_dir else Path(file_path)

    with open(file_path, **kwargs) as file_obj:
        function = _ALLOWED_FILE_READER_EXTENSION.get(file_path.suffix)
        return function(file_obj) if function is not None else file_obj.read()


def _read_internal_resource(relative_file_path):
    # read resources/file from files in the current module
    return read_file(resources.files(pkg_name) / relative_file_path)


if __name__ == "__main__":
    read_file("test.py")

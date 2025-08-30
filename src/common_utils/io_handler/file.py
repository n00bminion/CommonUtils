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
    Note that this doesn't directly create the file and returns actually the absolute file path

    Also it expects the file_path to be part of C drive and throws error if it isn't.
    This behaviour might need to be changed in the future tho...

    Args:
        file_path: string file path of the desired file path

    Return:
        Absolute Path object of the file_path
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
    """
    Read file and build the parent directories if needed.
    Note that there is a dictionary (_ALLOWED_FILE_READER_EXTENSION) of
    allow file type that can be opened but if the file is not
    of the allowed file type, will need to implement a function to do so.

    Args:
        file_path: string file path, can be relative or absolute
        build_parent_dir: boolean, set to true to build parent dirs otherwise it's defaulted to False
        **kwargs: Keyword arguments that can be passed in which will be used in the open() function when reading the file in

    Return:
        File content

    """
    file_path = prepare_file_path(file_path) if build_parent_dir else Path(file_path)

    with open(file_path, **kwargs) as file_obj:
        try:
            function = _ALLOWED_FILE_READER_EXTENSION.get(file_path.suffix)
        except KeyError:
            raise KeyError(
                f"File with extension '{file_path.suffix}' is not supported."
                f"The allowed extension are: {list(_ALLOWED_FILE_READER_EXTENSION.keys())}"
            )
        return function(file_obj) if function is not None else file_obj.read()


def _read_internal_resource(relative_file_path):
    """
    Read local resources files in this module. Not be used outside

    Args:
        relative_file_path: relative file path (from root) of the resource file
    """
    # read resources/file from files in the current module
    return read_file(resources.files(pkg_name) / relative_file_path)


if __name__ == "__main__":
    read_file("test.py")

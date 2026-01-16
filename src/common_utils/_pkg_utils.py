from common_utils.io_handler.file import read_file
from common_utils import __name__ as pkg_name
import importlib.resources as resources


def _read_internal_resource(relative_file_path):
    """
    Read local resources files in this module. Not to be used outside

    Args:
        relative_file_path: relative file path (from root) of the resource file

    Return:
        File content
    """
    # read resources/file from files in the current module
    return read_file(resources.files(pkg_name) / relative_file_path)

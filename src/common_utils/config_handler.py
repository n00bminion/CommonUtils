from common_utils.io_handler.file import read_file, prepare_file_path
from pathlib import Path


def get_config(config_file):
    # expect config file to be in config folder
    original_path = Path(config_file)
    default_path = Path(f"config/{original_path.name}")
    try:
        return read_file(default_path)
    except FileNotFoundError:
        print(
            f"Attempted to find file at '{default_path}' but failed. Now trying to read file using path passed in."
        )

    # or otherwise just pass in relative path to the file from cwd
    try:
        return read_file(original_path)
    except Exception as e:
        raise e

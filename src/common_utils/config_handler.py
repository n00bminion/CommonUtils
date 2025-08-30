from common_utils.io_handler.file import read_file
from pathlib import Path


def get_config(config_file):
    """
    Function to read in file in the config folder.
    If the file doesn't exist in config folder or the config folder doesn't exist,
    it try to read from the absolute path (if the absolute path was passed along with the file name)
    Finally, it will fail otherwise.

    Args:
        config_file: str path of the config file

    Return:
        config file content.
    """
    # expect config file to be in config folder
    original_path = Path(config_file)
    file_name = original_path.name

    for possible_path in (
        # config folder in top level
        Path(f"config/{file_name}"),
        # config folder is in src folder
        Path(f"src/config/{file_name}"),
        # finally just use the path passed in
        original_path,
    ):

        if possible_path.exists():
            break

        print(f"Tried to read file from {possible_path} but it does not exist.")

    try:
        # possible_path will be last item from the loop which is the actual path passed through
        return read_file(possible_path)
    except Exception as e:
        raise e

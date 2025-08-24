from pathlib import Path


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

from common_utils.io_handler.file import read_file
from pathlib import Path

POSSIBLE_CONFIG_PATHS = [
    "config/{file_name}",
    "src/config/{file_name}",
]


def get_config(config_file, check_possible_paths=True):
    """
    Function to return content of config file by checking the possible paths the config file might be in.
    This can be turned off by setting check_possible_paths to False and just use the path provided.
    Finally, it attempts to read the file but will fail if the file doesn't exist.

    Args:
        config_file: str path of the config file
        check_possible_paths: bool, check the possible paths the config file might be in

    Return:
        config file content.
    """
    # expect config file to be in config folder
    original_path = Path(config_file)

    if check_possible_paths:
        for possible_path_templates in POSSIBLE_CONFIG_PATHS + [config_file]:
            possible_path = Path(
                possible_path_templates.format(file_name=original_path.name),
            )
            if possible_path.exists():
                print(f"Successfully found config file at: '{possible_path}'.")
                break
    else:
        possible_path = original_path

    try:
        # possible_path will be last item from the loop which is the actual path passed through
        return read_file(possible_path)
    except Exception as e:
        raise e


if __name__ == "__main__":
    config = get_config("test.json")
    print(config)

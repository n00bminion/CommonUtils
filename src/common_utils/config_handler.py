from common_utils.io_handler.file import read_file
from pathlib import Path
import os


def _get_config_dir_in_src_pkg():
    cwd_path = Path(os.getcwd())

    src_dir = [f for f in cwd_path.iterdir() if ((f.is_dir()) and (f.name == "src"))]

    assert (
        len(src_dir) == 1
    ), f"{len(src_dir)} src directories found in current module... there should only be one."

    config_dir = [
        dir
        for pkg in src_dir[0].iterdir()
        for dir in pkg.iterdir()
        if dir.name == "config"
    ]

    # should be one or zero...
    no_of_config_dirs = len(config_dir)

    assert no_of_config_dirs in [
        0,
        1,
    ], f"{no_of_config_dirs} config directories found in current module... Unable to resolve which config folder to use. Try and collapse multiple config folders into one."

    if no_of_config_dirs:
        return config_dir[0]

    # return nothing otherwise, can't determine the config folder
    return


def get_config(config_file, check_possible_paths=True):
    """
    Function to return content of config file by checking the possible paths the config file might be in.

    The 3 places it scours are:
        - top level config, same level as src: ./config/
        - config folder 1 level down under src: ./src/config/
        - config folder 2 levels down under src: ./src/pkg_name/config/

    One caveat is when it looks for config file in ./src/pkg_name/config/, it looks at the current working directory and so if
    the function isn't running at the top level, it might not work that well...

    This can be turned off by setting check_possible_paths to False and it will use the path provided. It might also improve
    the speed of the function in cases where you have a large number of folders where it won't need to search about and just
    defaults to the path provided.

    Finally, it attempts to read the file but will fail if the file doesn't exist.

    Args:
        config_file: str path of the config file
        check_possible_paths: bool, check the possible paths the config file might be in

    Return:
        config file content.
    """

    possible_config_paths = [
        Path("config"),  # top level config, same level as src ./
        Path("src/config"),  # one level below so ./src/
        _get_config_dir_in_src_pkg(),  # this looks for config folder in ./src/pkg_name/
    ]

    original_path = Path(config_file)

    if check_possible_paths:
        for possible_path_templates in filter(
            lambda folder_template: bool(folder_template), possible_config_paths
        ):

            possible_path = Path(possible_path_templates) / original_path.name
            print(f"Trying to locate config file at: {possible_path}")

            if possible_path.exists():
                print(f"Successfully found config file at: '{possible_path}'.")
                break
        else:
            # defaults to the orignal path passed in if loops doesn't break
            possible_path = original_path

    else:
        # defaults to the original path is we choose it to
        possible_path = original_path

    try:
        # possible_path will be last item from the loop which is the actual path passed through
        return read_file(possible_path)
    except Exception as e:
        raise e


if __name__ == "__main__":
    get_config("test.json")

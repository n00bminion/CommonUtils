from common_utils.io_handler.file import read_file
from pathlib import Path
from importlib.resources import files


def _get_config_dir_in_src_pkg(module_name, config_folder_name):
    # if no module is passed in then we skip
    if not module_name:
        return

    module_path = Path(files(module_name))

    config_dir = [
        dir
        for dir in module_path.iterdir()
        if (dir.is_dir() and (dir.name == f"{config_folder_name}"))
    ]

    # should be one or zero...
    no_of_config_dirs = len(config_dir)

    assert no_of_config_dirs in [
        0,
        1,
    ], (
        f"{no_of_config_dirs} config directories found in current module... Unable to resolve which config folder to use. Try and collapse multiple config folders into one."
    )

    if no_of_config_dirs:
        return config_dir[0]

    # return nothing otherwise, can't determine the config folder
    return


def get_config(
    config_file,
    config_folder_name="config",
    module_name=None,
    check_possible_paths=True,
):
    """
    Function to return content of config file by checking the possible paths the config file might be in.

    The first 2 places it scours are:
        - top level config, same level as src: ./config/
        - config folder 1 level down under src: ./src/config/

    These two are mainly used for local code that are not supposed to be packaged up as when packaged up,
    anything outside of the src folder is excluded. However if developing locally and the config folder is set
    within the ./src/module_name/config/ folder, module_name is needed.

    The 3rd place it looks for is:
        - config folder 2 levels down under src: ./src/module_name/config/

    This is activated when the module_name argument is passed. You SHOULD use this when creating module
    that are supposed to be imported from other bits of code.

    If check_possible_paths is set to False and it will use the path provided. It might also improve
    the speed of the function in cases where you have a large number of folders where it won't need to search about and just
    defaults to the path provided.

    Finally, it attempts to read the file but will fail if the file doesn't exist.

    Args:
        config_file: str path of the config file
        config_folder_name: str name of the config folder
        module_name: str name of the module
        check_possible_paths: bool, check the possible paths the config file might be in

    Return:
        config file content.

    Example:
        >>> import module.__name__ as module_name
        >>> get_config(
                config_file = 'some_config_file_path.extension',
                module_name = module_name
                )
    """

    possible_config_paths = [
        # these two are for local modules
        Path(f"{config_folder_name}"),  # top level config, same level as src ./
        Path(f"src/{config_folder_name}"),  # one level below so ./src/
        # this is for import modules
        _get_config_dir_in_src_pkg(
            module_name, config_folder_name
        ),  # this looks for config folder in ./src/pkg_name/
    ]

    original_path = Path(config_file)

    if check_possible_paths:
        for possible_path_templates in filter(
            lambda folder_template: bool(folder_template), possible_config_paths
        ):
            possible_path = Path(possible_path_templates) / original_path.name

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
    get_config("test.yaml")

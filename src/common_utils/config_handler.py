import yaml
import json
from pathlib import Path
import os

_ALLOWED_CONFIG_FILE_EXTENSION = {
    ".yaml": yaml.safe_load,
    ".json": json.load,
}


def get_config(config_file):
    """
    Read the config file and return config as dictionary
    If used at the base of the project then relative path is fine
    """
    file_path = Path(config_file)
    config_file_extension = file_path.suffix

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} doesn't exist")

    if config_file_extension not in _ALLOWED_CONFIG_FILE_EXTENSION:
        raise ValueError("Invalid config file extension")

    with open(file_path) as stream:
        return _ALLOWED_CONFIG_FILE_EXTENSION[config_file_extension](stream)

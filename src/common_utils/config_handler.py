import yaml
import json
from pathlib import Path


def get_config(config_file):
    """
    Read the config file (use at base of project)
    and return config as dictionary
    """
    file_path = Path(config_file)
    config_file_extension = file_path.suffix

    with open(file_path) as stream:
        if config_file_extension == ".yaml":
            return yaml.safe_load(stream)
        elif config_file_extension == ".json":
            return json.load(stream)
        else:
            raise ValueError("Invalid config file extension")

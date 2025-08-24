from common_utils.io_handler.file import read_file


def get_config(config_file):
    return read_file(config_file)

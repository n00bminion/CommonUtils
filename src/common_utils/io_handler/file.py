from pathlib import Path
import shutil
import json
import yaml
import tomllib
import pypdf
import pandas as pd
import os
import pickle


class UnsupportedFileExtensionError(Exception):
    pass


# anything that's not implemented is defaulted to .read()/.write()
SUPPORTED_FILE_EXTENSION = {
    # specific func
    ".yaml": dict(
        read=yaml.safe_load,
        write=yaml.dump,
    ),
    ".json": dict(
        read=json.load,
        write=json.dump,
        pandas_write="to_json",
    ),
    ".toml": dict(
        read=tomllib.load,
        # hopefully we don't need to ever write toml...
    ),
    ".pdf": dict(
        read=pypdf.PdfReader,
    ),
    # default everything
    ".txt": dict(),
    ".sql": dict(),
    # tabular format so use pandas to read (might be better to use duckdb to read multiple files?)
    # use pandas to write so these get treated differently
    ".parquet": dict(
        read=pd.read_parquet,
        pandas_write="to_parquet",
    ),
    ".pkl": dict(
        read=pd.read_pickle,
        pandas_write="to_pickle",
        write=pickle.dump,
    ),
    ".pickle": dict(
        read=pd.read_pickle,
        pandas_write="to_pickle",
        write=pickle.dump,
    ),
    ".csv": dict(
        read=pd.read_csv,
        pandas_write="to_csv",
    ),
    ".xlsx": dict(
        read=pd.read_excel,
        pandas_write="to_excel",
    ),
}


def prepare_file_path(file_path):
    """
    If the directory (and it's subdirs) doesn't exist then it will get created.
    Note that this doesn't directly create the file and returns actually the absolute file path

    Also it expects the file_path to be part of C drive and throws error if it isn't.
    This behaviour might need to be changed in the future tho...

    Args:
        file_path: string file path of the desired file path

    Return:
        Absolute Path object of the file_path
    """
    # get absolute path
    save_path = Path(file_path).resolve()
    parent_dir = save_path.parent
    operating_system = os.name

    # expects file path to start with "C:\Users\name" or "D:\" on windows
    if operating_system == "nt":
        c_drive = Path.home().resolve()
        d_drive = Path("D:/")
        for drive_path in d_drive, c_drive:
            if parent_dir.is_relative_to(drive_path):
                break
        else:
            raise ValueError(
                f"{save_path} path should start with either '{c_drive}' or '{d_drive}'"
            )

    if operating_system == "linux":
        raise NotImplementedError(
            "common_utils.io_handler.file.prepare_file_path currently does not support running on Linux... Review and update the code accordingly."
        )

    # create the dir and any subdirs that doesn't exist
    parent_dir.mkdir(parents=True, exist_ok=True)

    return save_path


def remove_file(file_path):
    """
    Remove a file from location specified

    Args:
        file_path: string or pathlib.Path file path

    Return:
        None
    """

    Path(file_path).unlink(missing_ok=True)
    print(f"{file_path} is removed")


def remove_dir(dir_path):
    """
    Remove a folder from location specified (along with it's subdirs and contents)

    Args:
        dir_path: string or pathlib.Path directory path

    Return:
        None
    """
    dir_path = Path(dir_path)
    if dir_path.is_dir():
        shutil.rmtree(dir_path)
        return
    raise NotADirectoryError(f"{dir_path} is not a directory")


def read_file(
    file_path, build_parent_dir=False, open_mode="r", file_encoding=None, **kwargs
):
    """
    Read file and build the parent directories if needed.

    Args:
        file_path: string file path, can be relative or absolute
        build_parent_dir: boolean, set to true to build parent dirs otherwise it's defaulted to False
        open_mode: string mode to open file to write to, it's defaulted to "w"
        file_encoding: string encoding to open file to write to, it's defaulted to None
        **kwargs: Keyword arguments that can be passed in which will be used in the function reading the file

    Returns:
        File content

    """
    file_path = prepare_file_path(file_path) if build_parent_dir else Path(file_path)

    allowed_file_reader_extension = {
        k: v.get("read") for k, v in SUPPORTED_FILE_EXTENSION.items()
    }

    try:
        function = allowed_file_reader_extension[file_path.suffix]
    except KeyError:
        raise UnsupportedFileExtensionError(
            f"File with extension '{file_path.suffix}' is not supported for file reading. "
            f"The allowed extension are: {list(allowed_file_reader_extension.keys())}. "
            "Update SUPPORTED_FILE_EXTENSION in common_utils.io_handler.file to add support for this file extension."
        )

    if function.__module__.split(".")[0] == "pandas":
        return function(file_path, **kwargs)

    try:
        if file_path.suffix in [".pkl", ".pickle"] and "b" not in open_mode:
            new_open_mode = open_mode + "b"
            # ensure binary mode for pickle files
            print(
                f"Updated open_mode from '{open_mode}' to '{new_open_mode}' for pickle file reading"
            )
            open_mode = new_open_mode

        with open(file_path, mode=open_mode, encoding=file_encoding) as file_obj:
            return (
                function(file_obj, **kwargs)
                if function is not None
                else file_obj.read()
            )

    except Exception as e:
        print(f"Unable to read {file_path}")
        raise e


def save_to_file(
    content,
    file_path,
    build_parent_dir=True,
    open_mode="w",
    file_encoding=None,
    **kwargs,
):
    """
    Function to save some data/content to a file location (and build the parent directories if needed)

    Args:
        content: file content to be saved. This can be pretty much anything
        file_path: string file path, can be relative or absolute
        build_parent_dir: boolean, set to true to build parent dirs otherwise it's defaulted to False
        open_mode: string mode to open file to write to, it's defaulted to "w"
        file_encoding: string encoding to open file to write to, it's defaulted to None
        **kwargs: Keyword arguments that can be passed in which will be used in the function writing the file

    Return:
        None

    """

    # prep the file path to make sure the desire folder is there
    # this will raise error if it's not under root path
    file_path = prepare_file_path(file_path) if build_parent_dir else Path(file_path)
    allowed_file_writer_extension = {
        k: v.get("write") for k, v in SUPPORTED_FILE_EXTENSION.items()
    }

    allowed_pandas_file_writer_extension = {
        k: v.get("pandas_write")
        for k, v in SUPPORTED_FILE_EXTENSION.items()
        if v.get("pandas_write") is not None
    }

    if isinstance(content, pd.DataFrame):
        try:
            cls_method = allowed_pandas_file_writer_extension[file_path.suffix]
        except KeyError:
            raise UnsupportedFileExtensionError(
                f"File with extension '{file_path.suffix}' is not supported for pandas DataFrame writing. "
                f"The allowed extension are: {list(allowed_pandas_file_writer_extension.keys())}. "
                "Update SUPPORTED_FILE_EXTENSION in common_utils.io_handler.file to add support for this file extension."
            )

        getattr(content, cls_method)(file_path, **kwargs)

    else:
        try:
            if file_path.suffix in [".pkl", ".pickle"] and "b" not in open_mode:
                new_open_mode = open_mode + "b"
                # ensure binary mode for pickle files
                print(
                    f"Updated open_mode from '{open_mode}' to '{new_open_mode}' for pickle file reading"
                )
                open_mode = new_open_mode

            with open(
                file=file_path, mode=open_mode, encoding=file_encoding
            ) as file_obj:
                try:
                    function = allowed_file_writer_extension[file_path.suffix]
                except KeyError:
                    raise UnsupportedFileExtensionError(
                        f"File with extension '{file_path.suffix}' is not supported for file writing. "
                        f"The allowed extension are: {list(allowed_pandas_file_writer_extension.keys())}. "
                        "Update SUPPORTED_FILE_EXTENSION in common_utils.io_handler.file to add support for this file extension."
                    )

                return (
                    function(content, file_obj, **kwargs)
                    if function is not None
                    else file_obj.write(content)
                )

        # always wanna delete file if fail
        except Exception as e:
            print(f"Unable to write to {file_path}. Removing created file place holder")
            remove_file(file_path=file_path)
            raise e


if __name__ == "__main__":
    # read_file("test.py")
    # remove_dir("test")
    # save_to_file(
    #     pd.DataFrame({"a": [1, 2, 3]}),
    #     "abc.parquet",
    #     engine="pyarrow",
    # )

    # save_to_file("asdfadsfad", "xyz.adsf")  # this will fail

    print(read_file("abc.parquet"))

import os
from typing import Literal

from ranlib.constants import DOTRAN_FOLDER_NAME, PROJECT_ROOT

# NOTE: NO PATHS CAN END WITH A SLASH (/)
ROOT_PATH: str = ""


def DOTRAN_DIR_PATH() -> str:
    return f"{ROOT_PATH}/{DOTRAN_FOLDER_NAME}"


def RAN_TOML_PATH() -> str:
    return f"{ROOT_PATH}/ran.toml"


def LOCKFILE_PATH() -> str:
    return f"{ROOT_PATH}/{DOTRAN_FOLDER_NAME}/ran-lock.json"


def find_root_path() -> str | None:
    """Must be able to perfectly find the root path every single time"""
    current_path: str = os.getcwd()

    if len(ROOT_PATH) > 0 and current_path.startswith(ROOT_PATH):
        return ROOT_PATH

    dot_ranprojects_filepath: str = f"{PROJECT_ROOT}/.ranprojects"

    if not os.path.exists(dot_ranprojects_filepath):
        return None

    # Get the list of lines
    try:
        with open(dot_ranprojects_filepath, "r") as file:
            root_paths: list[str] = file.readlines()

        # Also return None if the length of the file is 0
        if len(root_paths) == 0:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    # Check which .ranprojects path is a substring of the current_path starting at 0
    for root_path in reversed(root_paths):  # start from the end for more recency
        if current_path.startswith(root_path):
            return root_path

    return None


def add_root_path(path: str):
    """Add a root path to the top of the .ranprojects file"""

    dot_ranprojects_filepath: str = f"{PROJECT_ROOT}/.ranprojects"

    try:
        # Read the current content to check if the file ends with a newline
        with open(dot_ranprojects_filepath, "a+") as file:
            file.seek(0)  # Move to the beginning of the file
            contents: str = file.read()

            # Determine if a newline is needed before appending the new line
            if contents and len(contents) > 0:
                file.write("\n")  # Add a newline if the current content does not end with one
            # Write the new line without leading or trailing newlines
            file.write(path)
    except Exception as e:
        print(f"An error occurred: {e}")


def set_root_path(root_path: str):
    global ROOT_PATH

    ROOT_PATH = root_path


def ran_toml_exists() -> bool:
    return os.path.exists(RAN_TOML_PATH())


def lockfile_exists() -> bool:
    return os.path.exists(LOCKFILE_PATH())


def dotran_dir_exists() -> bool:
    return os.path.exists(DOTRAN_DIR_PATH())


def get_ran_toml_path() -> str:
    global ROOT_PATH

    if not ran_toml_exists():
        ROOT_PATH = find_root_path()

    return RAN_TOML_PATH()


def get_lockfile_path() -> str:
    global ROOT_PATH

    if not lockfile_exists():
        ROOT_PATH = find_root_path()

    return LOCKFILE_PATH()


def get_dotran_dir_path() -> str:
    global ROOT_PATH

    if not dotran_dir_exists():
        ROOT_PATH = find_root_path()

    return DOTRAN_DIR_PATH()


# Class B existences (ones that you just want to read if exists, not read the whole thing or write to it)
# As a result, you must use find_root_path() instead of ROOT_PATH since there won't be a function setting that for us


def readme_exists() -> bool:
    return os.path.exists(f"{find_root_path()}/README.md")


def pixi_project_exists() -> bool:
    rootpath: str = find_root_path()

    return os.path.exists(f"{rootpath}/.pixi") or os.path.exists(f"{rootpath}/pixi.lock")


def environment_yml_exists(
    return_which: bool = False,
) -> bool | Literal["environment.yml", "environment.yaml"]:
    rootpath: str = find_root_path()

    if not return_which:
        return os.path.exists(f"{rootpath}/environment.yml") or os.path.exists(
            f"{rootpath}/environment.yaml"
        )
    else:
        if os.path.exists(f"{rootpath}/environment.yml"):
            return "environment.yml"
        elif os.path.exists(f"{rootpath}/environment.yaml"):
            return "environment.yaml"
        else:
            return False

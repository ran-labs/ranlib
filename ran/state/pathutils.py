import os


# NOTE: NO PATHS CAN END WITH A SLASH (/)
ROOT_PATH: str = ""


def DOTRAN_DIR_PATH() -> str:
    return f"{ROOT_PATH}/.ran"


def RAN_TOML_PATH() -> str:
    return f"{ROOT_PATH}/ran.toml"


def LOCKFILE_PATH() -> str:
    return f"{ROOT_PATH}/.ran/ran-lock.json"


# TODO:
def find_root_path() -> str:
    """Must be able to perfectly find the root path every single time"""
    pass


def ran_toml_exists() -> bool:
    return os.path.exists(RAN_TOML_PATH())


def lockfile_exists() -> bool:
    return os.path.exists(LOCKFILE_PATH())


def readme_exists() -> bool:
    return os.path.exists(f"{find_root_path()}/README.md")


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

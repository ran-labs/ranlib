import os

from typing import List, Dict, Union
from pydantic import BaseModel, Field

import tomli
import json

# This file is for the stuff having to do with state, being ran.toml the lockfile (.ran/ran-lock.json)

# Cannot end with a slash (/)
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


def get_ran_toml_path() -> str:
    global ROOT_PATH

    if ran_toml_exists():
        return RAN_TOML_PATH()
    else:
        ROOT_PATH = find_root_path()
        return RAN_TOML_PATH()


def get_lockfile_path() -> str:
    global ROOT_PATH

    if lockfile_exists():
        return LOCKFILE_PATH()
    else:
        ROOT_PATH = find_root_path()
        return LOCKFILE_PATH()


class RanDependency(BaseModel):
    paper_impl_id: str
    package_dependencies: List[str]


class RanLock(BaseModel):
    dependencies: List[RanDependency]

    # Post-resolution
    compilation_steps: List[str]  # change dtype of this later?
    resolved_package_dependencies: List[str]


# TODO:
def generate_lockfile():
    """Generate/Update a lockfile for the papers in .ran/ran-lock.json"""
    pass

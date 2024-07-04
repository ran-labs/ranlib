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


# ran.toml reqs

# For pushers [optional]
# RAN username
# paper name/id
# tag
# version
# description
# readme

# papers (just the paper implementations)

# settings
# package manager (either 'pip', 'pipx', 'uv', 'uvx', 'poetry', 'conda', 'mamba', 'micromamba', 'pipenv')
# package resolver (either 'auto' or 'isolate'). auto: if resolution fails, fallback to pipx/uvx (isolate mode)


class RanDependency(BaseModel):
    paper_impl_id: str  # for future: can be remote only
    package_dependencies: List[str]


class RanPackageDependency(BaseModel):
    package_name: str
    version: str
    isolated: bool = Field(default=False)


class RanLock(BaseModel):
    dependencies: List[RanDependency]

    # Post-resolution
    compilation_steps: List[str]  # change dtype of this later?
    resolved_package_dependencies: List[RanPackageDependency]

    # TODO:
    # (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is desccribed in ran_lock
    def run(self):
        """Above says it all. However, as compilation steps are done after receiving the stuff, they will be recorded and changed with this method"""
        pass


# TODO:
def generate_ran_toml():
    """Generate a fresh ran.toml"""
    pass


def read_lock() -> RanLock:
    """Find the lockfile and make a RanLock out of it"""
    with open(get_lockfile_path(), "r") as file:
        lockfile = json.load(file)

    ran_lock: RanLock = RanLock(**lockfile)
    return ran_lock


# TODO:
def produce_lock() -> RanLock:
    """Produce a RanLock from ran.toml (pre-resolve packages as well)"""
    pass


def apply_lock(lock: RanLock):
    # 1.) (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is desccribed in lock: RanLock
    lock.run()

    # 2.) Write to lockfile (yes, the above actually modified the RanLock)
    write_to_lockfile(lock)


# TODO:
def write_to_lockfile(lock: RanLock):
    pass

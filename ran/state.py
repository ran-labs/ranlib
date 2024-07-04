import os

from typing import List, Dict, Union
from pydantic import BaseModel, Field

import tomli
import tomli_w
import json

# RegEx
import re

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


def readme_exists() -> bool:
    return os.path.exists(f"{find_root_path()}/README.md")


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


# -- ran.toml reqs --


# For pushers [optional]
# RAN username
# paper name/id
# tag
# version
# description
# readme
class RanPlatformParams(BaseModel):
    # potential feature down the line: cache last user name and auto fill
    username: str = Field(default="")
    paper_id_name: str = Field(default="")  # e.g. 'attention_is_all_you_need'
    tag: str = Field(default="")
    version: str = Field(default="1")
    description: str = Field(default="")
    readme: str = Field(
        default_factory=(
            lambda: f"{find_root_path()}/README.md" if readme_exists() else ""
        )
    )


# settings
# package manager (either 'pip', 'pipx', 'uv', 'uvx', 'poetry', 'conda', 'mamba', 'micromamba', 'pipenv')
# package resolver (either 'auto' or 'isolate'). auto: if resolution fails, fallback to pipx/uvx (isolate mode)
class RanSettings(BaseModel):
    package_manager: str = Field(default="pip")
    isolate_dependencies: bool = Field(default=False)


class RanTOML(BaseModel):
    RAN: RanPlatformParams = Field(default=RanPlatformParams())

    # paper_impl_ids
    papers: str = Field(
        default="""
"""
    )  # fuck this formatter

    settings: RanSettings = Field(default=RanSettings())

    def deserialize_paper_impl_ids(self):
        return deserialize_paper_impl_ids(self.papers)


# Yeah, I'm gonna be a bitch about this unless the users complain
def deserialize_paper_impl_ids(paper_impl_ids: str) -> List[str]:
    # Example Before:
    """
    - attention_is_all_you_need
    - seanmeher/mamba
    - mae
    - rwkv:latest
    """

    # Example After:
    """
    ['attention_is_all_you_need', 'seanmeher/mamba', 'mae', 'rwkv:latest']
    """

    # Remove ALL whitespace
    paper_impl_ids_no_whitespace: str = re.sub(r"\s", "", paper_impl_ids)

    # Separate by hyphens
    paper_impl_ids_list: List[str] = paper_impl_ids_no_whitespace.split("-")

    return paper_impl_ids_list


def serialize_paper_impl_ids(paper_impl_ids: List[str]) -> str:
    # Example Before:
    """
    ['attention_is_all_you_need', 'seanmeher/mamba', 'mae', 'rwkv:latest']
    """

    # Example After:
    """
    - attention_is_all_you_need
    - seanmeher/mamba
    - mae
    - rwkv:latest
    """

    draft: str = "\n- ".join(paper_impl_ids)

    # Now add it to the first as well
    serialized_paper_impl_ids: str = "\n- " + draft

    return serialized_paper_impl_ids


def generate_ran_toml():
    """Generate a fresh ran.toml"""

    # Make the string to write to the ran.toml file
    ran_toml_obj: RanTOML = RanTOML()
    ran_dot_toml: str = tomli_w.dumps(ran_toml_obj.dict(), multiline_strings=True)

    # Write it to the ran.toml file
    file_path: str = get_ran_toml_path()
    with open(file_path, "w") as file:
        file.write(ran_dot_toml)

    print("Generated ran.toml")


def read_ran_toml() -> RanTOML:
    """Find ran.toml and make a RanTOML out of it"""
    with open(get_ran_toml_path(), "rb") as file:
        ran_toml_dict: Dict = tomli.load(file)

    ran_toml: RanTOML = RanTOML(**ran_toml_dict)
    return ran_toml


# -- RAN LOCK STUFF (LOCKFILE) --
class RanDependency(BaseModel):
    paper_impl_id: str  # for future: can be remote only
    package_dependencies: List[str]


class RanPackageDependency(BaseModel):
    package_name: str
    version: str
    isolated: bool


class RanLock(BaseModel):
    dependencies: List[RanDependency]

    # Post-pre-resolution stuff below

    # The key is the paper_impl_id
    # The value is the list of commands to run as 'compilation'
    compilation_steps: Dict[str, List[str]]

    resolved_package_dependencies: List[RanPackageDependency]

    # TODO:
    # (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is desccribed in ran_lock
    def run(self):
        """Above says it all. However, as compilation steps are done after receiving the stuff, they will be recorded and changed with this method"""
        # And if something gets recompiled, the compilation steps WILL be replaced
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
    ran_toml: RanTOML = read_ran_toml()

    paper_impl_ids: List[str] = ran_toml.deserialize_paper_impl_ids()

    package_manager: str = ran_toml.settings.package_manager
    isolate_dependencies: bool = ran_toml.settings.isolate_dependencies

    # TODO: pre-resolution

    # Get previous compilation steps (tree)
    prev_ran_lock: RanLock = read_lock()
    prev_compilation_steps: Dict[str, List[str]] = prev_ran_lock.compilation_steps

    ran_lock: RanLock = RanLock(
        dependencies=[],  # TODO:
        compilation_steps=prev_compilation_steps,  # Will be elaborated on a following step
        resolved_package_dependencies=[],  # TODO:
    )

    return ran_lock


def apply_lock(lock: RanLock):
    # 1.) (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is desccribed in lock: RanLock
    lock.run()

    # 2.) Write to lockfile (yes, the above actually modified the RanLock)
    write_to_lockfile(lock)


def write_to_lockfile(lock: RanLock):
    """Write to .ran/ran-lock.json"""
    ran_lock_dot_json: Dict = lock.dict()

    file_path: str = get_lockfile_path()
    with open(file_path, "w") as file:
        json.dump(ran_lock_dot_json, file)

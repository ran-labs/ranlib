import os

from typing import List, Dict, Set, Union
from pydantic import BaseModel, Field

import tomli
import tomli_w
import json

# RegEx
import re

from cli.info_retrieval import fetch_dependencies
from cli import preresolution

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


class PaperInstallation(BaseModel):
    paper_impl_id: str
    isolate: bool
    # remote_only: bool


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

    # Yeah, I'm gonna be a bitch about this unless the users complain
    def deserialize_paper_installations(self) -> List[PaperInstallation]:
        """
        Isolation Notation: 'isolate:' or 'noisolate:'

        Example - isolate:ameerarsala/rwkv:latest
        """

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
        paper_impl_ids_no_whitespace: str = re.sub(r"\s", "", self.papers)

        # Separate by hyphens
        paper_impl_ids_list: List[str] = paper_impl_ids_no_whitespace.split("-")

        # Read isolation notation
        paper_installations: List[PaperInstallation] = []
        for paper_impl_id in paper_impl_ids_list:
            isolation: bool = self.settings.isolate_dependencies  # Default value
            if paper_impl_id.startswith("isolate:"):
                isolation = True
            elif paper_impl_id.startswith("noisolate:"):
                isolation = False

            paper_installation: PaperInstallation = PaperInstallation(
                paper_impl_id=paper_impl_id,
                isolate=isolation,
            )
            paper_installations.append(paper_installation)

        return paper_installations


# TODO: make it generate off the lock from default if exists
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
class PythonPackageDependency(BaseModel):
    package_name: str
    version: str
    isolated: bool


class RanPaperInstallation(BaseModel):
    paper_impl_id: str
    package_dependencies: List[PythonPackageDependency]


class RanLock(BaseModel):
    ran_paper_installations: List[RanPaperInstallation]

    # Post-pre-resolution stuff below

    # The key is the paper_impl_id
    # The value is the list of commands to run as 'compilation'
    compilation_steps: Dict[str, List[str]]

    preresolved_python_dependencies: List[PythonPackageDependency]

    def empty():
        return RanLock(
            ran_paper_installations=[],
            compilation_steps={},
            preresolved_package_dependencies=[],
        )

    def get_paper_impl_ids(self):
        return [
            paper_installation.paper_impl_id
            for paper_installation in self.ran_paper_installations
        ]

    def get_as_paper_installations(self) -> List[PaperInstallation]:
        return [
            PaperInstallation(
                paper_impl_id=ran_paper_installation.paper_impl_id,
                isolate=ran_paper_installation.package_dependencies[0].isolated,
            )  # isolation happens as a group
            for ran_paper_installation in self.ran_paper_installations
        ]

    # TODO:
    # (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is desccribed in ran_lock
    def run(self):
        """Above says it all. However, as compilation steps are done after receiving the stuff, they will be recorded and changed with this method"""
        # And if something gets recompiled (perhaps due to a different package version?), the compilation steps WILL be replaced (desired behavior)
        pass


class DeltaLockData(BaseModel):
    paper_impl_ids: List[str]
    ran_paper_installations: List[RanPaperInstallation]
    pypackage_dependencies: List[PythonPackageDependency]


class DeltaRanLock(BaseModel):
    to_add: DeltaLockData
    to_remove: DeltaLockData
    final_ran_paper_installations: List[RanPaperInstallation]


# On Adding: pretty obvious; the only stuff that will be installed though is from preresolved_python_dependencies
# On Removing: deletes the associated modules and compilation steps, uninstalls the isolated packages that nobody depends on anymore
def produce_delta_lock() -> DeltaRanLock:
    """Produce a DeltaRanLock from ran.toml (pre-resolve packages as well)"""
    ran_toml: RanTOML = read_ran_toml()
    prev_ran_lock: RanLock = read_lock()

    paper_installations: List[PaperInstallation] = (
        ran_toml.deserialize_paper_installations()
    )

    prev_paper_installations: List[PaperInstallation] = (
        prev_ran_lock.get_as_paper_installations()
    )

    # paper_impl_ids: List[str] = [paper.paper_impl_id for paper in paper_installations]
    #
    # paper_impl_ids_set: Set[str] = set(paper_impl_ids)
    # prev_paper_impl_ids_set: Set[str] = set(prev_ran_lock.get_paper_impl_ids())
    #
    # # Used to add/remove compilation steps as well
    # to_add_paper_impl_ids: Set[str] = paper_impl_ids_set - prev_paper_impl_ids_set
    # to_remove_paper_impl_ids: Set[str] = prev_paper_impl_ids_set - paper_impl_ids_set

    paper_installations_set: Set[PaperInstallation] = set(paper_installations)
    prev_paper_installations_set: Set[PaperInstallation] = set(prev_paper_installations)

    # Used to extract paper_impl_ids which is used to add/remove compilation steps as well
    to_add_paper_installations: Set[PaperInstallation] = (
        paper_installations_set - prev_paper_installations_set
    )
    to_remove_paper_installations: Set[PaperInstallation] = (
        prev_paper_installations_set - paper_installations_set
    )

    # Extract paper_impl_ids
    to_add_paper_impl_ids: Set[str] = set(
        [
            paper_installation.paper_impl_id
            for paper_installation in to_add_paper_installations
        ]
    )
    to_remove_paper_impl_ids: Set[str] = set(
        [
            paper_installation.paper_impl_id
            for paper_installation in to_remove_paper_installations
        ]
    )

    # Create RanPaperInstallation's
    to_add_ranpaperinstallations: List[RanPaperInstallation] = fetch_dependencies(
        to_add_paper_installations
    )
    to_remove_ranpaperinstallations: List[RanPaperInstallation] = [
        ran_paper_installation
        for ran_paper_installation in prev_ran_lock.ran_paper_installations
        if ran_paper_installation.paper_impl_id in to_remove_paper_impl_ids
    ]

    ran_paper_installations: List[RanPaperInstallation] = list(
        set(prev_ran_lock.ran_paper_installations)
        + set(to_add_ranpaperinstallations)
        - set(to_remove_ranpaperinstallations)
    )

    # Pre-resolution
    preresolved_pkg_deps: List[PythonPackageDependency] = (
        preresolution.preresolve_dependencies(ran_paper_installations)
    )
    prev_preresolved_pkg_deps: List[PythonPackageDependency] = (
        prev_ran_lock.preresolved_package_dependencies
    )

    # Now, preresolution!
    (to_add_pkg_deps, to_remove_pkg_deps) = preresolution.resolve_to_deltas(
        preresolved_pkg_deps, prev_preresolved_pkg_deps
    )

    return DeltaRanLock(
        to_add=DeltaLockData(
            paper_impl_ids=list(to_add_paper_impl_ids),
            ran_paper_installations=to_add_ranpaperinstallations,
            pypackage_dependencies=to_add_pkg_deps,
        ),
        to_remove=DeltaLockData(
            paper_impl_ids=list(to_remove_paper_impl_ids),
            ran_paper_installations=to_remove_ranpaperinstallations,
            pypackage_dependencies=to_remove_pkg_deps,
        ),
        final_ran_paper_installations=ran_paper_installations,
    )


def read_lock() -> RanLock:
    """Find the lockfile and make a RanLock out of it"""
    try:
        with open(get_lockfile_path(), "r") as file:
            lockfile = json.load(file)

        ran_lock: RanLock = RanLock(**lockfile)
        return ran_lock
    except FileNotFoundError:
        # Return an empty lock
        return RanLock.empty()


def apply_lock(lock: RanLock):
    # 0.) Get the delta lock to apply
    # delta_lock: DeltaRanLock = lock.subtract(lock_prev)

    # 1.) (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is described in lock: RanLock
    lock.run()

    # 2.) Write to lockfile (yes, the above actually modified the RanLock)
    write_to_lockfile(lock)


def write_to_lockfile(lock: RanLock):
    """Write to .ran/ran-lock.json"""
    ran_lock_dot_json: Dict = lock.dict()

    file_path: str = get_lockfile_path()
    with open(file_path, "w") as file:
        json.dump(ran_lock_dot_json, file)

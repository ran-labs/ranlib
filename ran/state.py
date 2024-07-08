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

from __init__ import __version__

from constants import DEFAULT_ISOLATION_VALUE

# This file is for the stuff having to do with state, being ran.toml the lockfile (.ran/ran-lock.json)

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


# -- .ran/ --
def generate_dotran_dir():
    dotran_dir_path: str = get_dotran_dir_path()

    # Generate .ran/ directory and .ran/ran_modules directory
    try:
        os.makedirs(dotran_dir_path, exist_ok=True)
        print("Directory '.ran/' created successfully.")

        os.makedirs(f"{dotran_dir_path}/ran_modules", exist_ok=True)
        print("Directory '.ran/ran_modules' created successfully.")
    except OSError as error:
        print(f"Directory '.ran/' cannot be created successfully. Error: {error}")

    # Generate a RANFILE (.ran/ran_modules/RANFILE) [lightweight lil file that doesnt do much]
    with open(f"{dotran_dir_path}/ran_modules/RANFILE", "w") as ranfile:
        ranfile.write(f"RANLIB Version {__version__}")


# Rest of stuff
class PaperImplID(BaseModel):
    author: str
    paper_id: str
    processed_tag: str  # cannot just be "latest" as that is before processing

    def from_str(paper_impl_id: str):
        """Create a PaperImplID object from its string version."""
        slash_idx: int = paper_impl_id.index("/")  # for author
        colon_idx: int = paper_impl_id.rindex(":")  # for tag

        author: str = paper_impl_id[0:slash_idx]
        paper_id: str = paper_impl_id[slash_idx + 1 : colon_idx]
        processed_tag: str = paper_impl_id[colon_idx + 1 :]

        return PaperImplID(
            author=author, paper_id=paper_id, processed_tag=processed_tag
        )

    def __str__(self) -> str:
        return f"{self.author}/{self.paper_id}:{self.processed_tag}"


def paper_impl_ids_equal(paper_impl_id: str, paper_impl_id2: str) -> bool:
    pass


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
    isolate_dependencies: bool = Field(default=DEFAULT_ISOLATION_VALUE)


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
            paper_impl_id_: str = str(paper_impl_id)  # copy it

            isolation: bool = self.settings.isolate_dependencies  # Default value
            if paper_impl_id.startswith("isolate:"):
                isolation = True
                paper_impl_id_ = paper_impl_id_[len("isolate:") :]
            elif paper_impl_id.startswith("noisolate:"):
                isolation = False
                paper_impl_id_ = paper_impl_id_[len("noisolate:")]

            paper_installation: PaperInstallation = PaperInstallation(
                paper_impl_id=paper_impl_id_,
                isolate=isolation,
            )
            paper_installations.append(paper_installation)

        return paper_installations

    def serialize_paper_installations(
        paper_installations: List[PaperInstallation],
    ) -> str:
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

        serialized_papers: str = ""

        for paper in paper_installations:
            paper_impl_id: str = ""

            if paper.isolate:
                paper_impl_id += "isolate:"
            else:
                paper_impl_id += "noisolate:"

            paper_impl_id += paper.paper_impl_id

            serialized_papers += f"\n- {paper_impl_id}"

        return serialized_papers

    def add_paper_installations(self, paper_installations: List[PaperInstallation]):
        # Serialize
        new_papers_serialized: str = RanTOML.serialize_paper_installations(
            paper_installations
        )

        # Add 'em
        self.papers = "".join([self.papers, "\n", new_papers_serialized])

    # Do this by paper_impl_id
    def remove_paper_installations(self, to_remove_paper_impl_ids: List[str]):
        # Deserialize to get existing
        installed_papers: List[PaperInstallation] = (
            self.deserialize_paper_installations()
        )

        # Installed Papers' (prime)
        _installed_papers_: List[PaperInstallation] = [
            installed_paper
            for installed_paper in installed_papers
            if installed_paper.paper_impl_id not in to_remove_paper_impl_ids
        ]

        # Reserialize and set
        self.papers = RanTOML.serialize_paper_installations(_installed_papers_)


def generate_ran_toml():
    """Generate a fresh ran.toml. If the lockfile exists, it will generate off that."""

    # Make the string to write to the ran.toml file
    ran_toml_obj: RanTOML = RanTOML()

    if lockfile_exists():
        # Generate off the lockfile
        ran_lock: RanLock = read_lock()
        ran_toml_obj.papers = RanTOML.serialize_paper_installations(
            ran_lock.get_as_paper_installations()
        )

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


def write_to_ran_toml(ran_toml: RanTOML):
    """Write to ran.toml"""
    ran_dot_toml: str = tomli_w.dumps(ran_toml.dict(), multiline_strings=True)

    file_path: str = get_ran_toml_path()
    with open(file_path, "w") as file:
        file.write(ran_dot_toml)


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


class DeltaLockData(BaseModel):
    paper_impl_ids: List[str]
    ran_paper_installations: List[RanPaperInstallation]
    pypackage_dependencies: List[PythonPackageDependency]

    def empty():
        return DeltaLockData(
            paper_impl_ids=[], ran_paper_installations=[], pypackage_dependencies=[]
        )


class DeltaRanLock(BaseModel):
    to_add: DeltaLockData
    to_remove: DeltaLockData

    final_ran_paper_installations: List[RanPaperInstallation]
    prev_ran_lock: RanLock

    # TODO:
    # (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is described in ran_lock
    def run_and_produce_updated_lock(self) -> RanLock:
        """Above says it all. However, as compilation steps are done after receiving the stuff, they will be recorded and changed with this method"""
        # This assumes post-preresolution of what should be added and removed
        # And if something gets recompiled (perhaps due to a different package version?), the compilation steps WILL be replaced (desired behavior)
        # TODO: Also postprocess the paper_impl_ids that are being added into their actual verbose values (for maximum reproducibility)
        pass


# On Adding: pretty obvious; the only stuff that will be installed though is from preresolved_python_dependencies
# On Removing: deletes the associated modules and compilation steps, uninstalls the isolated packages that nobody depends on anymore
def produce_delta_lock(paper_installations: List[PaperInstallation]) -> DeltaRanLock:
    """Produce a DeltaRanLock from paper installations (pre-resolve packages as well)"""
    prev_ran_lock: RanLock = read_lock()

    prev_paper_installations: List[PaperInstallation] = (
        prev_ran_lock.get_as_paper_installations()
    )

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
        prev_ran_lock=prev_ran_lock,
    )


def produce_delta_lock_from_ran_toml(ran_toml: RanTOML):
    """Produce a DeltaRanLock from ran.toml (pre-resolve packages as well)"""
    paper_installations: List[PaperInstallation] = (
        ran_toml.deserialize_paper_installations()
    )

    return produce_delta_lock(paper_installations)


def produce_delta_lock_from_ran_lock(ran_lock: RanLock):
    """Produce a DeltaRanLock from a RanLock (pre-resolve packages as well)"""
    paper_installations: List[PaperInstallation] = ran_lock.get_as_paper_installations()

    return produce_delta_lock(paper_installations)


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


def apply_delta_lock(delta_lock: DeltaRanLock):
    # 1.) (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is described in lock: RanLock
    lock: RanLock = delta_lock.run_and_produce_updated_lock()

    # 2.) Write to lockfile (yes, the above actually modified the RanLock)
    write_to_lockfile(lock)


def apply_ran_toml(ran_toml: RanTOML):
    # 0.) Make a DeltaRanLock
    delta_ran_lock: DeltaRanLock = produce_delta_lock_from_ran_toml(ran_toml)

    # 1.) Apply the DeltaRanLock
    apply_delta_lock(delta_ran_lock)


def apply_lock(lock: RanLock):
    # 0.) Make a DeltaRanLock
    delta_ran_lock: DeltaRanLock = produce_delta_lock_from_ran_lock(lock)

    # 1.) Apply the DeltaRanLock
    apply_delta_lock(delta_ran_lock)


def write_to_lockfile(lock: RanLock):
    """Write to .ran/ran-lock.json"""
    ran_lock_dot_json: Dict = lock.dict()

    file_path: str = get_lockfile_path()
    with open(file_path, "w") as file:
        json.dump(ran_lock_dot_json, file)


def generate_ran_lock():
    """Generate a fresh .ran/ran-lock.json. If the ran.toml exists, it will generate off that."""

    if ran_toml_exists():
        ran_toml: RanTOML = read_ran_toml()

        apply_ran_toml(ran_toml)
    else:
        # Generate a fresh one
        ran_lock: RanLock = RanLock.empty()

        # Write it to the lockfile
        write_to_lockfile(ran_lock)

    print("Generated lockfile")

"""This file is about the ran.toml file (manifest) and lockfile"""

import json
import uuid
from typing import Literal, Self, Union

import tomli
import tomli_w
from git import Repo
from pydantic import BaseModel, Field

from ranlib.compilation import compiler
from ranlib.constants import (
    DEFAULT_ISOLATION_VALUE,
    RAN_DEFAULT_AUTHOR_NAME,
)

# , RAN_MODULES_FOLDER_NAME
from ranlib.state.pathutils import (
    get_dotran_dir_path,
    get_lockfile_path,
    get_ran_toml_path,
    lockfile_exists,
    # find_root_path,
    # readme_exists,
    ran_toml_exists,
)


class PaperImplID(BaseModel):
    author: str
    paper_id: str
    tag: str

    @classmethod
    def from_str(cls, paper_impl_id: str) -> Self:
        """Create a PaperImplID object from its string version."""

        slash_idx: int = paper_impl_id.find("/")  # for author
        colon_idx: int = paper_impl_id.rfind(":")  # for tag

        author_specified: bool = slash_idx != -1
        tag_specified: bool = colon_idx != -1

        author: str = paper_impl_id[0:slash_idx] if author_specified else RAN_DEFAULT_AUTHOR_NAME
        tag: str = paper_impl_id[colon_idx + 1 :] if tag_specified else "latest"

        id_start: int = slash_idx + 1 if author_specified else 0
        id_end: int = colon_idx if tag_specified else len(paper_impl_id)

        paper_id: str = paper_impl_id[id_start:id_end]

        return cls(author=author, paper_id=paper_id, tag=tag)

    def __str__(self) -> str:
        return f"{self.author}/{self.paper_id}:{self.tag}"

    def __eq__(self, other):
        # Check if 'other' is an instance of the same class
        if isinstance(other, PaperImplID):
            return (
                self.paper_id == other.paper_id
                and self.author == other.author
                and self.tag == other.tag
            )

        return False

    def __hash__(self) -> int:
        return hash((self.author, self.paper_id, self.tag))


class PaperInstallation(BaseModel):
    paper_impl_id: PaperImplID
    isolate: bool
    # remote_only: bool


# -- ran.toml reqs --
def generate_default_tag_hash() -> str:
    return str(uuid.uuid4())[:13].replace("-", "")


# For pushers [optional]
# RAN username
# paper name/id
# tag
# description
class RanPlatformParams(BaseModel):
    # potential feature down the line: cache last user name and auto fill
    username: str = Field(default="")
    paper_id_name: str = Field(default="")  # e.g. 'attention_is_all_you_need'
    tag: str = Field(default_factory=generate_default_tag_hash)
    description: str = Field(default="")
    repo_url: str = Field(default="")  # TODO: auto-fill if a git url is detected


# Dependencies
class RanPaperDependencies(BaseModel):
    # paper_impl_ids
    papers: list[str] = Field(default=[])


# settings
# package manager (either 'pip', 'pipx', 'uv', 'uvx', 'poetry', 'conda', 'mamba', 'micromamba', 'pipenv')
# package resolver (either 'auto' or 'isolate'). auto: if resolution fails, fallback to pipx/uvx (isolate mode)
class RanSettings(BaseModel):
    isolate_dependencies: bool = Field(default=DEFAULT_ISOLATION_VALUE)


# Field names are intentional and correspond to the TOML file
class RanTOML(BaseModel):
    RAN: RanPlatformParams = Field(default=RanPlatformParams())

    dependencies: RanPaperDependencies = Field(default=RanPaperDependencies())

    settings: RanSettings = Field(default=RanSettings())

    def read_paper_installations(self) -> list[PaperInstallation]:
        """
        Example Before:
        ['attention_is_all_you_need', 'seanmeher/mamba', 'mae', 'rwkv:latest']

        Example After:
        [PaperInstallation(), ...]

        Isolation Notation: 'isolate:' or 'noisolate:'
        Example - isolate:ameerarsala/rwkv:latest
        """

        paper_impl_ids_list: list[str] = self.dependencies.papers

        # Read isolation notation
        paper_installations: list[PaperInstallation] = []
        for paper_impl_id in paper_impl_ids_list:
            paper_impl_id_: str = str(paper_impl_id)  # copy it
            paper_impl_id_ = paper_impl_id_.replace(" ", "")  # remove any remaining whitespace

            isolation: bool = self.settings.isolate_dependencies  # Default value
            if paper_impl_id.startswith("isolate:"):
                isolation = True
                paper_impl_id_ = paper_impl_id_[len("isolate:") :]
            elif paper_impl_id.startswith("noisolate:"):
                isolation = False
                paper_impl_id_ = paper_impl_id_[len("noisolate:") :]

            paper_installation: PaperInstallation = PaperInstallation(
                paper_impl_id=PaperImplID.from_str(paper_impl_id_),
                isolate=isolation,
            )
            paper_installations.append(paper_installation)

        return paper_installations

    def write_paper_installations(self, paper_installations: list[PaperInstallation]) -> list[str]:
        """
        Example Before:
        [PaperInstallation(), ...]

        Example After:
        ['attention_is_all_you_need', 'seanmeher/mamba', 'mae', 'rwkv:latest']
        """

        serialized_papers: list[str] = []
        isolate_by_default: bool = self.settings.isolate_dependencies

        for paper in paper_installations:
            paper_impl_id: str = ""

            if isolate_by_default and not paper.isolate:
                paper_impl_id += "noisolate:"
            elif not isolate_by_default and paper.isolate:
                paper_impl_id += "isolate:"

            paper_impl_id += str(paper.paper_impl_id)

            serialized_papers.append(paper_impl_id)

        return serialized_papers

    def set_paper_installations(self, paper_installations: list[PaperInstallation]):
        # Serialize
        serialized_papers: list[str] = self.write_paper_installations(paper_installations)

        # Set 'em
        self.dependencies.papers = serialized_papers

    def add_paper_installations(self, paper_installations: list[PaperInstallation]):
        # Serialize
        new_papers_serialized: list[str] = self.write_paper_installations(paper_installations)

        # Add 'em
        self.dependencies.papers += new_papers_serialized

    # Do this by paper_impl_id
    def remove_paper_installations(self, to_remove_paper_impl_ids: list[PaperImplID]):
        # Read to get existing
        installed_papers: list[PaperInstallation] = self.read_paper_installations()

        # Installed Papers' (prime)
        # Filter for the ones that are not in to_remove_paper_impl_ids
        _installed_papers_: list[PaperInstallation] = [
            installed_paper
            for installed_paper in installed_papers
            if installed_paper.paper_impl_id not in to_remove_paper_impl_ids
        ]

        # Reserialize and update
        self.dependencies.papers = self.write_paper_installations(_installed_papers_)


def generate_ran_toml():
    """Generate a fresh ran.toml. If the lockfile exists, it will generate off that."""

    # Make the string to write to the ran.toml file
    ran_toml_obj: RanTOML = RanTOML()

    if lockfile_exists():
        # Generate off the lockfile
        ran_lock: RanLock = read_lock()
        ran_toml_obj.set_paper_installations(ran_lock.get_as_paper_installations())

    ran_dot_toml: str = tomli_w.dumps(ran_toml_obj.dict(), multiline_strings=False)

    # Write it to the ran.toml file
    file_path: str = get_ran_toml_path()
    with open(file_path, "w") as file:
        file.write(ran_dot_toml)

    print("Generated ran.toml")


def read_ran_toml() -> RanTOML:
    """Find ran.toml and make a RanTOML out of it"""
    with open(get_ran_toml_path(), "rb") as file:
        ran_toml_dict: dict = tomli.load(file)

    ran_toml: RanTOML = RanTOML(**ran_toml_dict)
    return ran_toml


def write_to_ran_toml(ran_toml: RanTOML):
    """Write to ran.toml"""
    ran_dot_toml: str = tomli_w.dumps(ran_toml.dict(), multiline_strings=False)

    file_path: str = get_ran_toml_path()
    with open(file_path, "w") as file:
        file.write(ran_dot_toml)


# -- RAN LOCK STUFF (LOCKFILE) --


class PackageVersion(BaseModel):
    lower_bound: str
    upper_bound: str

    @classmethod
    def from_str(cls, version_str: str) -> Self:
        """Create a PackageVersion object from its string version."""
        if version_str.startswith("="):
            if version_str.startswith("=="):
                lower_bound: str = version_str[2:]
            else:
                lower_bound: str = version_str[1:]

            upper_bound: str = lower_bound
        elif version_str.startswith(">="):
            lower_bound: str = version_str[2:]
            upper_bound: str = version_str[version_str.find(",") + 1 :]
        else:
            raise ValueError("Invalid version string")

        return cls(lower_bound=lower_bound, upper_bound=upper_bound)

    def __hash__(self) -> int:
        return hash((self.lower_bound, self.upper_bound))

    def as_installable_str(self, is_pypi: bool) -> str:
        if self.lower_bound != self.upper_bound:
            return f">={self.lower_bound},<{self.upper_bound}"

        # Otherwise, they are =
        equals: str = ""
        if is_pypi:
            equals = "=="
        else:
            equals = "="

        return equals + self.lower_bound

    def __str__(self) -> str:
        if self.lower_bound == self.upper_bound:
            return "=" + self.lower_bound
        else:
            return f">={self.lower_bound},<{self.upper_bound}"


class PythonPackageDependency(BaseModel):
    package_name: str
    version: PackageVersion  # This should not be a range, but given the nature of the pixi.toml files, it probably will be
    package_type: Literal["pypi", "non-pypi"]  # Non-pypi is for conda-like stuff
    channel: str  # For non-pypi
    isolated: bool

    def __hash__(self) -> int:
        return hash(
            (
                self.package_name,
                self.version,
                self.package_type,
                self.channel,
                self.isolated,
            )
        )

    def __str__(self) -> str:
        # Other than beginning with 'isolate:' or 'noisolate:', the rest is the same as a shell install
        # This will also not include whether it is pypi or not explicitly, but can implicitly be seen since the conda channels will always be shown
        # Therefore, if there is no channel, it is a pypi package

        isolation: str = "isolate" if self.isolated else "noisolate"

        dependency_str: str = self.package_name + self.version.as_installable_str(
            self.package_type == "pypi"
        )

        if self.package_type == "non-pypi" and self.channel != "":
            dependency_str = self.channel + "::" + dependency_str

        # Example: isolate:"conda-forge::numpy=1.23.1" or noisolate:"conda-forge::numpy>=1.23.1,<1.24.0"
        return f'{isolation}:"{dependency_str}"'


class RanPaperInstallation(BaseModel):
    paper_impl_id: PaperImplID
    package_dependencies: list[PythonPackageDependency]

    def __hash__(self) -> int:
        return hash((self.paper_impl_id, *self.package_dependencies))


class RanLock(BaseModel):
    ran_paper_installations: list[RanPaperInstallation]

    # Post-pre-resolution stuff below

    # The key is the paper_impl_id
    # The value is the list of commands to run as 'compilation'
    compilation_steps: dict[str, list[str]]

    preresolved_python_dependencies: list[PythonPackageDependency]

    def empty():
        return RanLock(
            ran_paper_installations=[],
            compilation_steps={},
            preresolved_python_dependencies=[],
        )

    def get_as_paper_installations(self) -> list[PaperInstallation]:
        return [
            PaperInstallation(
                paper_impl_id=ran_paper_installation.paper_impl_id,
                isolate=ran_paper_installation.package_dependencies[0].isolated,
            )  # isolation happens as a group. If 1 dep is isolated, the whole paper and all of its dependencies will be counted as such
            for ran_paper_installation in self.ran_paper_installations
        ]


class DeltaLockData(BaseModel):
    ran_paper_installations: list[RanPaperInstallation]
    pypackage_dependencies: list[PythonPackageDependency]  # post-preresolution

    def empty():
        return DeltaLockData(
            paper_impl_ids=[], ran_paper_installations=[], pypackage_dependencies=[]
        )

    def get_paper_impl_ids(self) -> list[PaperImplID]:
        return [
            ran_paper_installation.paper_impl_id
            for ran_paper_installation in self.ran_paper_installations
        ]

    def get_paper_impl_ids_strs(self) -> list[str]:
        return [
            str(ran_paper_installation.paper_impl_id)
            for ran_paper_installation in self.ran_paper_installations
        ]

    def get_paper_ids(self) -> list[str]:
        return [
            ran_paper_installation.paper_impl_id.paper_id
            for ran_paper_installation in self.ran_paper_installations
        ]


class DeltaRanLock(BaseModel):
    to_add: DeltaLockData
    to_remove: DeltaLockData

    final_ran_paper_installations: list[RanPaperInstallation]
    prev_ran_lock: RanLock

    def make_ran_lock(self, compilation_steps: dict[str, list[str]]) -> RanLock:
        prev_deps_set = frozenset(self.prev_ran_lock.preresolved_python_dependencies)
        to_add_deps_set = frozenset(self.to_add.pypackage_dependencies)
        to_remove_deps_set = frozenset(self.to_remove.pypackage_dependencies)
        preresolved_python_dependencies: list[PythonPackageDependency] = list(
            prev_deps_set.union(to_add_deps_set).difference(to_remove_deps_set)
        )

        return RanLock(
            ran_paper_installations=self.final_ran_paper_installations,
            compilation_steps=compilation_steps,
            preresolved_python_dependencies=preresolved_python_dependencies,
        )

    # (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is described in ran_lock
    def run_and_produce_updated_lock(self) -> RanLock:
        """Above says it all. However, as compilation steps are done after receiving the stuff, they will be recorded and changed with this method"""
        # This assumes post-preresolution of what should be added and removed
        # And if something gets recompiled (perhaps due to a different package version?), the compilation steps WILL be replaced (desired behavior)
        import ranlib.state.dependencies.package_installation as pkgs
        from ranlib.state.dependencies.paper_info_retrieval import fetch_repo_url

        compilation_steps: dict[str, list[str]] = {}

        # Step 0: precompilation - setup the new and cleanup the old
        print("Precompiling...")
        compiler.precompile(
            to_add_paper_ids=self.to_add.get_paper_ids(),
            to_remove_paper_ids=self.to_remove.get_paper_ids(),
        )

        # Next, install and remove packages
        print("Updating packages...")

        pkgs.remove(self.to_remove.pypackage_dependencies)

        pkgs.install(self.to_add.pypackage_dependencies)

        # First, clone and compile/transpile each paper. Compilation steps should be yielded as a result
        print("Fetching and compiling papers...")
        for ran_paper_installation in self.final_ran_paper_installations:
            paper_impl_id: PaperImplID = ran_paper_installation.paper_impl_id
            key: str = str(paper_impl_id)
            if ran_paper_installation in self.to_add.ran_paper_installations:
                # Clone & compile/transpile the paper
                ran_modules_path: str = f"{get_dotran_dir_path()}"
                repo_url: str = fetch_repo_url(paper_impl_id)

                cloned_folder_name: str = ran_paper_installation.paper_impl_id.paper_id
                cloned_folder_path: str = f"{ran_modules_path}/{cloned_folder_name}"
                Repo.clone_from(repo_url, cloned_folder_path)

                # Add to compilation steps to be yielded as a result
                comp_steps: list[str] = compiler.compile(
                    paper_id=ran_paper_installation.paper_impl_id.paper_id,
                    compilation_parent_dir=ran_modules_path,
                    compilation_target_subdir=cloned_folder_name,
                )

                compilation_steps[key] = comp_steps
            elif ran_paper_installation not in self.to_remove.ran_paper_installations:
                # These are the ones that are kept (so not added or removed)
                compilation_steps[key] = self.prev_ran_lock.compilation_steps[key]

        # After compilation on each paper, run this to clear the cache
        compiler.postcompilation()

        # Now, make the RanLock
        print("Generating lock from deltas...")
        return self.make_ran_lock(compilation_steps=compilation_steps)


# On Adding: pretty obvious; the only stuff that will be installed though is from preresolved_python_dependencies
# On Removing: deletes the associated modules and compilation steps, uninstalls the isolated packages that nobody depends on anymore
def produce_delta_lock(
    paper_installations: list[PaperInstallation],
    prev_lock: RanLock = None,
) -> DeltaRanLock:
    """
    Produce a DeltaRanLock from paper installations (pre-resolve packages as well)

    paper_installations are not necessarily just the ADDED installations but the state of new installations as a whole which INCLUDES those to add
    """

    # I HATE PYTHON
    from ranlib.state.dependencies import preresolution
    from ranlib.state.dependencies.paper_info_retrieval import fetch_dependencies

    prev_ran_lock: RanLock = None
    if prev_lock is not None:
        prev_ran_lock = prev_lock
    else:
        prev_ran_lock: RanLock = read_lock()

    prev_ran_paper_installations: list[RanPaperInstallation] = (
        prev_ran_lock.ran_paper_installations
    )

    # First thing's first: to the fetching HERE before anything else
    # Here's what it's gotta do:
    # 0.) Process tags like 'latest' into their actual values
    # 1.) Fetch the dependencies based on that and wrap in a nice RanPaperInstallation
    ran_paper_installations: list[RanPaperInstallation] = fetch_dependencies(paper_installations)

    ran_paper_installations_set: frozenset[RanPaperInstallation] = frozenset(
        ran_paper_installations
    )
    prev_ran_paper_installations_set: frozenset[RanPaperInstallation] = frozenset(
        prev_ran_paper_installations
    )

    # Create deltas for RanPaperInstallation's
    to_add_ran_paper_installations: list[RanPaperInstallation] = list(
        ran_paper_installations_set - prev_ran_paper_installations_set
    )
    to_remove_ran_paper_installations: list[RanPaperInstallation] = list(
        prev_ran_paper_installations_set - ran_paper_installations_set
    )

    # Pre-resolution

    # Domestic preresolution
    preresolved_pkg_deps: list[PythonPackageDependency] = preresolution.preresolve_dependencies(
        ran_paper_installations
    )
    prev_preresolved_pkg_deps: list[PythonPackageDependency] = (
        prev_ran_lock.preresolved_python_dependencies
    )

    # Inter-preresolution
    (to_add_pkg_deps, to_remove_pkg_deps) = preresolution.resolve_to_deltas(
        preresolved_pkg_deps, prev_preresolved_pkg_deps
    )

    return DeltaRanLock(
        to_add=DeltaLockData(
            ran_paper_installations=to_add_ran_paper_installations,
            pypackage_dependencies=to_add_pkg_deps,
        ),
        to_remove=DeltaLockData(
            ran_paper_installations=to_remove_ran_paper_installations,
            pypackage_dependencies=to_remove_pkg_deps,
        ),
        final_ran_paper_installations=ran_paper_installations,
        prev_ran_lock=prev_ran_lock,
    )


def produce_delta_lock_from_ran_toml(ran_toml: RanTOML, prev_lock: RanLock = None) -> DeltaRanLock:
    """Produce a DeltaRanLock from ran.toml (pre-resolve packages as well)"""
    paper_installations: list[PaperInstallation] = ran_toml.read_paper_installations()

    return produce_delta_lock(paper_installations, prev_lock=prev_lock)


def produce_delta_lock_from_ran_lock(ran_lock: RanLock, prev_lock: RanLock = None) -> DeltaRanLock:
    """Produce a DeltaRanLock from a RanLock (pre-resolve packages as well)"""
    paper_installations: list[PaperInstallation] = ran_lock.get_as_paper_installations()

    return produce_delta_lock(paper_installations, prev_lock=prev_lock)


def apply_delta_lock(delta_lock: DeltaRanLock):
    """Applies changes within the project and writes them to a lockfile"""

    # 1.) (Clone + Compile/Transpile if needed), Package installation. Literally just follow what is described in lock: RanLock
    lock: RanLock = delta_lock.run_and_produce_updated_lock()

    # 2.) Write to lockfile (yes, the above actually modified the RanLock)
    write_to_lockfile(lock)


def apply_ran_toml(ran_toml: RanTOML, from_zero: bool = False, write_to_randottoml: bool = True):
    prev_lock: RanLock = None
    if from_zero:
        prev_lock = RanLock.empty()

    # 1.) Make a DeltaRanLock
    delta_ran_lock: DeltaRanLock = produce_delta_lock_from_ran_toml(ran_toml, prev_lock=prev_lock)

    # 2.) Apply the DeltaRanLock
    apply_delta_lock(delta_ran_lock)

    # 3.) Write to RanTOML
    if write_to_randottoml:
        write_to_ran_toml(ran_toml)


def apply_lock(lock: RanLock, from_zero: bool = False):
    prev_lock: RanLock = None
    if from_zero:
        prev_lock = RanLock.empty()
    # no need for an else statement here since produce_delta_lock will automatically get the prior lock if it's not specified as anything but None

    # 1.) Make a DeltaRanLock
    delta_ran_lock: DeltaRanLock = produce_delta_lock_from_ran_lock(lock, prev_lock=prev_lock)

    # 2.) Apply the DeltaRanLock
    apply_delta_lock(delta_ran_lock)


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


def write_to_lockfile(lock: RanLock):
    """Write to .ran/ran-lock.json"""
    ran_lock_dot_json: dict = lock.dict()

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

    print("Generated lockfile.")

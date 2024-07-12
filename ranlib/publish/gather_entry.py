"""
Gather an entry be pushed to the registry
Here's how to use:
    # Gather the dependencies
    dependencies: List[str] = gather_dependencies()
    
    # Write the dependencies to the RANFILE
    ranfile: RANFILE = RANFILE(python_dependencies=dependencies)
    ranfile.write_to_ranfile()
    
    # Get the registry entry
    registry_entry: RegistryPaperImplEntry = gather_registry_entry(dependencies)

    # Then push this to the remote registry
    # Afterwards, push to the git remote
"""

import os

from typing import List, Dict
from pydantic import BaseModel, Field

import tomli

# Registry object
from state.paper_info_retrieval import PaperImplementationVersion

from state.ranstate import (
    PaperImplID,
    RanTOML,
    RanLock,
    PackageManager,
    PythonPackageDependency,
)
from state.ranstate import read_ran_toml, read_lock

from state.pathutils import find_root_path
from state import package_installation as pypkgs

from cli.utils import init_pixi_project

from publish import dependency_parsing as dep_parsing


class RegistryPaperImplEntry(BaseModel):
    paper_id: str
    username: str

    paper_impl_version: PaperImplementationVersion

    def as_paper_impl_id(self) -> PaperImplID:
        return PaperImplID(
            author=self.username,
            paper_id=self.paper_id,
            tag=self.paper_impl_version.tag,
        )


# To be pushed
def gather_registry_entry(dependencies: List[str]) -> RegistryPaperImplEntry:
    ran_toml: RanTOML = read_ran_toml()

    paper_id: str = ran_toml.RAN.paper_id_name
    username: str = ran_toml.RAN.username

    description: str = ran_toml.RAN.description

    tag: str = ran_toml.RAN.tag
    repo_url: str = ran_toml.RAN.repo_url

    registry_entry: RegistryPaperImplEntry = RegistryPaperImplEntry(
        paper_id=paper_id,
        username=username,
        paper_impl_version=PaperImplementationVersion(
            tag=tag,
            repo_url=repo_url,
            description=description,
            dependencies=dependencies,
        ),
    )

    return registry_entry


# str() a List of PythonPackageDependency because it will format correctly
def gather_dependencies() -> List[str]:
    """
    Auto-figure out the dependencies to be put in the RANFile; prioritize in order of:
        - pixi.toml
        - environment.yml (conda, mamba, micromamba); actually, on pushing, a lock WILL be generated of this by switching to pixi with https://prefix.dev/blog/pixi_a_fast_conda_alternative
        - pyproject.toml (pixi)
        - pyproject.toml (poetry)
        - pyproject.toml (pdm)
        - requirements.txt (pip, uv, etc. even pipenv can utilize this)
    """
    # Figure out the dependencies
    dependencies: List[PythonPackageDependency] = []

    root_path: str = find_root_path()

    if os.path.exists(f"{root_path}/environment.yml"):
        # Create a pixi project; make it someone else's problem!!!
        init_pixi_project()

    # In all cases, add all to `dependencies`
    if os.path.exists(f"{root_path}/pixi.toml"):
        dependencies += _parse_pixi_dot_toml(root_path)

    if os.path.exists(f"{root_path}/pyproject.toml"):
        # Parse all 3 forms
        dependencies += _parse_pyproject_dot_toml(root_path)

    if os.path.exists(f"{root_path}/requirements.txt"):
        dependencies += _parse_requirements_dot_txt(root_path)

    # Remove duplicates
    dependencies = list(frozenset(dependencies))

    # Turn it into strs
    dependencies_strs: List[str] = [str(dependency) for dependency in dependencies]

    return dependencies_strs


def _parse_pixi_dot_toml(root_path: str) -> List[PythonPackageDependency]:
    pass


def _parse_pyproject_dot_toml(root_path: str) -> List[PythonPackageDependency]:
    """
    Parse all forms:
        - (pixi)
        - (poetry)
        - (pdm)
    """
    pass


def _parse_requirements_dot_txt(root_path: str) -> List[PythonPackageDependency]:
    # Possibly look into pipenv source to see how they did it?
    pass

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
from state.ranfile import RANFILE, read_ranfile

from state.pathutils import find_root_path
from state import package_installation as pypkgs

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


# Stringify a List of PythonPackageDependency because it will format correctly
def gather_dependencies() -> List[str]:
    """
    Auto-figure out the dependencies to be put in the RANFile; prioritize in order of:
        - [COMING SOON] pixi.lock
        - environment.yml (conda, mamba, micromamba); actually, on pushing, a lock WILL be generated of this by switching to pixi with https://prefix.dev/blog/pixi_a_fast_conda_alternative
        - [NOT SUPPORTED RN] poetry.lock (poetry)
        - [NOT SUPPORTED RN] pdm.lock (pdm)
        - [NOT SUPPORTED RN] Pipfile.lock (pipenv)
        - requirements.txt (pip, uv, etc.)
        - ran-lock.json (ran; can also see which are isolated here)
        then manually (going around the python files and checking their imports)
    """
    # Figure out the dependencies
    dependencies: List[str] = []

    root_path: str = find_root_path()
    #ran_toml: RanTOML = read_ran_toml()
    
    # Assume all packages are from the specified package manager unless there's a library imported that was never specified via the respective dependency/lockfile in which case default to pip or uv if that's specified
    # Get ALL dependencies from the respective dependency file
    #if package_manager == "poetry":
        # Search for poetry.lock
    #    pass
    #elif package_manager == "pipenv":
        # Search for Pipfile.lock
    #    pass
    #else:
        # Assume pip / uv
    #    pass

        # Search for requirements.txt

        # Also add on everything from ran-lock.json

"""
Gather an entry be pushed to the registry
Here's how to use:
    # Gather the dependencies
    dependencies: list[str] = gather_dependencies()

    # Write the dependencies to the RANFILE
    ranfile: RANFILE = RANFILE(python_dependencies=dependencies)
    ranfile.write_to_ranfile()

    # Get the registry entry
    registry_entry: RegistryPaperImplEntry = gather_registry_entry(dependencies)

    # Then push this to the remote registry
    # Afterwards, push to the git remote
"""

import os
from typing import Union

import tomli
from pydantic import BaseModel, Field

from ranlib.cli.helpers import manifest_pixi_project
from ranlib.state.dependencies import package_installation as pypkgs

# Registry object
from ranlib.state.dependencies.paper_info_retrieval import PaperImplementationVersion
from ranlib.state.pathutils import environment_yml_exists, find_root_path
from ranlib.state.ranstate import (
    PackageVersion,
    PaperImplID,
    PythonPackageDependency,
    RanLock,
    RanTOML,
    read_lock,
    read_ran_toml,
)


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
def gather_registry_entry(dependencies: list[str]) -> RegistryPaperImplEntry:
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
def gather_dependencies() -> list[str]:
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
    dependencies: list[PythonPackageDependency] = []

    root_path: str = find_root_path()

    if environment_yml_exists():
        # Manifest a pixi project; make it someone else's problem!!!
        # If one already exists, it won't initialize one
        manifest_pixi_project()

    # In all cases, add all to `dependencies`
    if os.path.exists(f"{root_path}/pixi.toml"):
        dependencies += _read_pixi_dot_toml(root_path)

    if os.path.exists(f"{root_path}/pyproject.toml"):
        # Parse all 3 forms
        dependencies += _read_pyproject_dot_toml(root_path)

    if os.path.exists(f"{root_path}/requirements.txt"):
        dependencies += _read_requirements_dot_txt(root_path)

    # Remove duplicates
    dependencies = list(frozenset(dependencies))

    # Turn it into strs
    dependencies_strs: list[str] = [str(dependency) for dependency in dependencies]

    return dependencies_strs


def _read_pixi_dot_toml(root_path: str) -> list[PythonPackageDependency]:
    dependencies: list[PythonPackageDependency] = []

    with open(f"{root_path}/pixi.toml", "rb") as file:
        pixi_toml: dict = tomli.load(file)

    # Non-pypi Packages
    default_channel: str = pixi_toml["project"]["channels"][0]

    if pixi_toml.get("dependencies") is not None:
        for pkg_name, value in pixi_toml["dependencies"].items():
            channel: str = ""
            version: str = ""
            if isinstance(value, str):
                version = value
                channel = default_channel
            else:
                # Dict assumed
                version = value["version"]
                channel = value["channel"]

            dependencies.append(
                PythonPackageDependency(
                    package_name=pkg_name,
                    version=PackageVersion.from_str(version),
                    package_type="non-pypi",
                    channel=channel,
                    isolated=False,  # don't isolate on push
                )
            )

    # Pypi packages
    if pixi_toml.get("pypi-dependencies") is not None:
        for pkg_name, version in pixi_toml["pypi-dependencies"].items():
            dependencies.append(
                PythonPackageDependency(
                    package_name=pkg_name,
                    version=PackageVersion.from_str(version),
                    package_type="pypi",
                    channel="",  # empty when pypi
                    isolated=False,  # don't isolate on push
                )
            )


# TODO: pyproject.toml (for pixi and poetry)
def _read_pyproject_dot_toml(root_path: str) -> list[PythonPackageDependency]:
    """
    Parse all forms:
        - [COMING SOON] (pixi)
        - (poetry)
        - Not gonna support pdm due to conflicts with pixi
    """
    dependencies: list[PythonPackageDependency] = []

    # Read pyproject.toml
    with open(f"{root_path}/pixi.toml", "rb") as file:
        pyproject_toml: dict = tomli.load(file)

    tool: dict = pyproject_toml.get("tool")

    # TODO:
    # Try pixi's pyproject.toml for pypi packages
    # project: Dict = pyproject_toml.get("project")
    # if project is not None and project.get("dependencies") is not None:
    #     for

    # TODO:
    # Try pixi's pyproject.toml for non-pypi packages

    # Try poetry's pyproject.toml
    poetry: dict = tool.get("poetry")
    if poetry is not None and poetry.get("dependencies") is not None:
        for pkg_name, ver in poetry["dependencies"].items():
            version: str = ver.replace("^", ">=")

            dependencies.append(
                PythonPackageDependency(
                    package_name=pkg_name,
                    version=PackageVersion.from_str(version),
                    package_type="pypi",
                    channel="",  # empty when pypi
                    isolated=False,  # don't isolate on push
                )
            )


# TODO: requirements.txt
def _read_requirements_dot_txt(root_path: str) -> list[PythonPackageDependency]:
    # Possibly look into pipenv source to see how they did it?
    return []

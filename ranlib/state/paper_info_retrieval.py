import os
import shutil

from typing import List, Dict, Set, Union, Literal
from pydantic import BaseModel, Field

from state.ranstate import PaperInstallation, PaperImplID
from state.ranstate import RanPaperInstallation, PythonPackageDependency, PackageVersion

from constants import (
    LIB_ROOT,
    RAN_REGISTRY_GIT_HTTPS_URL,
    RAN_DEFAULT_AUTHOR_NAME,
    DEFAULT_ISOLATION_VALUE,
)

from git import Repo
import yaml

import re


# Example registry.yaml
"""
attention_is_all_you_need:
    randefault:
        versions:
            - tag: v1
              repo_url: https://github.com/...
              dependencies:
                  - numpy==1.23.1
                  - pandas==...
    ameerarsala:
        versions:
            ...
    
    seanmeher:
        versions:
            ...
"""


class PaperImplementationVersion(BaseModel):
    tag: str
    repo_url: str
    description: str
    dependencies: List[str]

    def as_python_package_dependencies(
        self, force_isolation: bool
    ) -> List[PythonPackageDependency]:
        """
        Parse the dependencies: List[str] -> List[PythonPackageDependency]

        isolation will only be enforced if force_isolation is True
        """

        pypackage_deps: List[PythonPackageDependency] = []

        # NOTE: Each dependency MUST start with either 'isolate:' or 'noisolate:'
        for dependency_ in self.dependencies:
            default_isolation: bool = DEFAULT_ISOLATION_VALUE
            package_start_idx: int = 0

            # trim all whitespace
            dependency: str = re.sub(r"\s+", "", dependency_)
            dependency = dependency.replace('"', "")  # remove any quotation marks

            """
            Example `dependency`:
                noisolate:"conda-forge::numpy>=1.23.1,<1.24.0"
            """

            if dependency.startswith("isolate:"):
                default_isolation = True
                package_start_idx = len("isolate:")
            elif dependency.startswith("noisolate:"):
                default_isolation = False
                package_start_idx = len("noisolate:")

            version: PackageVersion = None
            version_start_idx: int = 0

            equals_idx: int = dependency.index("=")
            if dependency.find("=") != -1:
                version_start_idx = equals_idx
            elif dependency.find(">=") != -1:
                version_start_idx = dependency.find(">=")

            version = PackageVersion.from_str(dependency[version_start_idx:])

            package_type: Literal["pypi", "non-pypi"] = "non-pypi"
            channel: str = ""
            if "::" in dependency[package_start_idx:version_start_idx]:
                package_type = "non-pypi"

                # NOTE: It is important that things go in this order
                channel_divider_idx: int = dependency.index("::")
                channel = dependency[package_start_idx:channel_divider_idx]

                package_start_idx = channel_divider_idx + 2
            else:
                package_type = "pypi"

            package_name: str = dependency[package_start_idx:version_start_idx]
            isolated: bool = force_isolation or default_isolation

            pypackage_deps.append(
                PythonPackageDependency(
                    package_name=package_name,
                    version=version,
                    package_type=package_type,
                    channel=channel,
                    isolated=isolated,
                )
            )

        return pypackage_deps


def load_registry(update_registry: bool = True) -> Dict:
    if update_registry:
        print("Retrieving Latest Registry...")
        shutil.rmtree(f"{LIB_ROOT}/ran-registry", ignore_errors=True)

        # Clone
        Repo.clone_from(
            RAN_REGISTRY_GIT_HTTPS_URL, f"{LIB_ROOT}/ran-registry"
        )  # clones into LIB_ROOT/ran-registry/*

    with open(f"{LIB_ROOT}/ran-registry/registry.yaml") as registry_file:
        registry: Dict = yaml.safe_load(registry_file)

    return registry


def _find_matching_version_idx(versions: List[Dict], nametag: str) -> int:
    for idx, version in enumerate(versions):
        if version["tag"] == nametag:
            return idx

    return -1


def fetch_paper_implementation_version(
    paper_impl_id: PaperImplID, registry: Dict
) -> PaperImplementationVersion:
    versions: List[Dict] = registry[paper_impl_id.paper_id][paper_impl_id.author][
        "versions"
    ]

    # Get correct version index based on
    idx: int = 0
    if paper_impl_id.tag == "latest":
        idx = -1
    elif paper_impl_id.tag == "earliest":
        idx = 0
    else:
        # This implies the tag is exact
        # Find idx by nametag
        idx = _find_matching_version_idx(versions, paper_impl_id.tag)

    version: PaperImplementationVersion = PaperImplementationVersion(**versions[idx])

    return version


def fetch_repo_url(paper_impl_id: PaperImplID, update_registry: bool = False) -> str:
    registry: Dict = load_registry(update_registry)

    version: PaperImplementationVersion = fetch_paper_implementation_version(
        paper_impl_id, registry
    )

    return version.repo_url


def fetch_dependencies(
    paper_installations: List[PaperInstallation], update_registry: bool = True
) -> List[RanPaperInstallation]:
    """
    Fetch from remote to get the required python package names and versions, then return the as List[RanPaperInstallation]

    Actually, for now we could just have a public git repo to be pulled from that would contain all the papers as yaml or json
    """
    # 0.) Git clone latest, which consists of removing the existing one then git cloning
    # 1.) Read locally and process tags like 'latest' into their actual values (their actual verbose values for maximum reproducibility)
    registry: Dict = load_registry(update_registry=update_registry)

    # Fetch dependencies
    ran_paper_installations: List[RanPaperInstallation] = []
    for paper_installation in paper_installations:
        paper_impl_id: PaperImplID = paper_installation.paper_impl_id
        isolate_packages: bool = paper_installation.isolate

        version: PaperImplementationVersion = fetch_paper_implementation_version(
            paper_impl_id, registry
        )

        # Process tags like 'latest' and 'earliest' into their respective tags
        # (Use EXACT tag, no aliases)
        paper_impl_id.tag = version.tag

        # Fetch dependencies
        package_dependencies: List[PythonPackageDependency] = (
            version.as_python_package_dependencies(force_isolation=isolate_packages)
        )

        ran_paper_installations.append(
            RanPaperInstallation(
                paper_impl_id=paper_impl_id, package_dependencies=package_dependencies
            )
        )

    return ran_paper_installations

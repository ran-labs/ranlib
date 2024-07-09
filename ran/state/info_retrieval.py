import os
import shutil

from typing import List, Dict, Set, Union
from pydantic import BaseModel, Field

from state.ranstate import PaperInstallation, PaperImplID
from state.ranstate import RanPaperInstallation, PythonPackageDependency

from constants import LIB_ROOT, RAN_REGISTRY_GIT_HTTPS_URL, RAN_DEFAULT_AUTHOR_NAME

from git import Repo
import yaml


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
    dependencies: List[str]

    def as_python_package_dependencies(
        self, isolated: bool
    ) -> List[PythonPackageDependency]:
        pypackage_deps: List[PythonPackageDependency] = []

        for dependency in self.dependencies:
            equals_idx: int = dependency.index("==")

            package_name: str = dependency[0:equals_idx]
            version: str = dependency[equals_idx + 2 :]

            pypackage_deps.append(
                PythonPackageDependency(
                    package_name=package_name, version=version, isolated=isolated
                )
            )

        return pypackage_deps


def load_registry(update_registry: bool = True) -> Dict:
    if update_registry:
        print("Updating Registry...")
        try:
            shutil.rmtree(f"{LIB_ROOT}/ran-registry")
        except OSError:
            pass

        # Clone
        Repo.clone_from(
            RAN_REGISTRY_GIT_HTTPS_URL, LIB_ROOT
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
    Fetch from DB to get the required python package names and versions, then return the as List[RanPaperInstallation]

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
            version.as_python_package_dependencies(isolate_packages)
        )

        ran_paper_installations.append(
            RanPaperInstallation(
                paper_impl_id=paper_impl_id, package_dependencies=package_dependencies
            )
        )

    return ran_paper_installations

import json
from typing import Literal, Union

import httpx
from pydantic import BaseModel, Field

from ranlib.constants import DEFAULT_ISOLATION_VALUE, RAN_API_SERVER_URL, RAN_DEFAULT_AUTHOR_NAME
from ranlib.state.ranstate import (
    PackageVersion,
    PaperImplID,
    PaperInstallation,
    PythonPackageDependency,
    RanPaperInstallation,
)
from ranlib.utils import remove_all_whitespace

# Example registry.yaml [DEPRECATED]
"""
attention_is_all_you_need:
    $randefault:
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
    dependencies: list[str]

    def as_python_package_dependencies(
        self, forced_isolation_value: bool | None = None
    ) -> list[PythonPackageDependency]:
        """
        Parse the dependencies: List[str] -> List[PythonPackageDependency]

        isolation will only be enforced if force_isolation is True
        """

        pypackage_deps: list[PythonPackageDependency] = []

        # NOTE: Each dependency MUST start with either 'isolate:' or 'noisolate:'
        # Go thru a denormalization process
        for _dependency_ in self.dependencies:
            """
            Example `_dependency_`:
                noisolate:"conda-forge::numpy>=1.23.1,<1.24.0"
            """

            default_isolation: bool = DEFAULT_ISOLATION_VALUE
            package_start_idx: int = 0

            # trim all whitespace
            _dependency: str = remove_all_whitespace(_dependency_)
            _dependency = _dependency.replace('"', "")  # remove any quotation marks

            if _dependency.startswith("isolate:"):
                default_isolation = True
                package_start_idx = len("isolate:")
            elif _dependency.startswith("noisolate:"):
                default_isolation = False
                package_start_idx = len("noisolate:")

            # Denormalization complete
            dependency: str = _dependency[package_start_idx:]

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
            if "::" in dependency[:version_start_idx]:
                package_type = "non-pypi"

                # NOTE: It is important that things go in this order
                channel_divider_idx: int = dependency.index("::")
                channel = dependency[:channel_divider_idx]

                package_start_idx = channel_divider_idx + 2
            else:
                package_type = "pypi"

            package_name: str = dependency[:version_start_idx]
            isolated: bool = (
                forced_isolation_value if forced_isolation_value is not None else default_isolation
            )

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


def fetch_paper_implementation_version(paper_impl_id: PaperImplID) -> PaperImplementationVersion:
    # Make a POST request to RAN_API_SERVER_URL
    response = httpx.post(
        url=f"{RAN_API_SERVER_URL}/v1/read_registry",
        headers={"Content-Type": "application/json"},
        data=json.dumps(paper_impl_id.dict()),
    )

    if not response.is_success:
        # Failure
        raise Exception("Paper Implementation Not Found")

    # Success
    json_response: dict = response.json()
    version: PaperImplementationVersion = PaperImplementationVersion(**json_response)

    return version


def fetch_repo_url(paper_impl_id: PaperImplID) -> str:
    version: PaperImplementationVersion = fetch_paper_implementation_version(paper_impl_id)

    return version.repo_url


def fetch_dependencies(paper_installations: list[PaperInstallation]) -> list[RanPaperInstallation]:
    """
    Fetch from remote to get the required python package names and versions, then return the as List[RanPaperInstallation]

    Actually, for now we could just have a public git repo to be pulled from that would contain all the papers as yaml or json
    """
    # Read locally and process tags like 'latest' into their actual values (their actual verbose values for maximum reproducibility)

    # Fetch dependencies
    ran_paper_installations: list[RanPaperInstallation] = []
    for paper_installation in paper_installations:
        paper_impl_id: PaperImplID = paper_installation.paper_impl_id
        isolate_packages: bool = paper_installation.isolate

        version: PaperImplementationVersion = fetch_paper_implementation_version(paper_impl_id)

        # Process tags like 'latest' and 'earliest' into their respective tags
        # (Use EXACT tag, no aliases)
        paper_impl_id.tag = version.tag

        # Fetch dependencies
        package_dependencies: list[PythonPackageDependency] = (
            version.as_python_package_dependencies(forced_isolation_value=isolate_packages)
        )

        ran_paper_installations.append(
            RanPaperInstallation(
                paper_impl_id=paper_impl_id, package_dependencies=package_dependencies
            )
        )

    return ran_paper_installations

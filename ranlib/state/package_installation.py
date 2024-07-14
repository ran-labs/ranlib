from typing import List, Dict, Set, Union, Tuple
from pydantic import BaseModel, Field

import subprocess

from state.ranstate import PythonPackageDependency, read_ran_toml, RanTOML


# TODO: Enforce isolation


def _stringify_packages(
    packages: List[PythonPackageDependency],
    include_versions: bool = True,
    separator: str = " ",
) -> str:
    pkgs_str: str = ""
    for package in packages:
        package_str: str = str(package)

        # For now, remove the isolation notation
        # NOTE: Order matters here
        package_str = package_str.replace("noisolate:", "")
        package_str = package_str.replace("isolate:", "")

        pkgs_str += package_str + separator

    return pkgs_str


def pre_run():
    # Use the correct pixi shell to avoid errors
    subprocess.run("pixi shell --change-ps1=false", shell=True, check=True)


def install(packages: List[PythonPackageDependency]):
    num_packages: int = len(packages)
    if num_packages == 0:
        print("No packages to install.")
        return

    pre_run()

    # Install the packages
    print("Installing Packages...")

    # Install the non-pypi packages
    conda_packages: List[PythonPackageDependency] = [
        package for package in packages if package.package_type == "non-pypi"
    ]
    if len(conda_packages) > 0:
        subprocess.run(
            f"pixi add {_stringify_packages(conda_packages)}", shell=True, check=True
        )

    # Install the pypi packages
    pypi_packages: List[PythonPackageDependency] = [
        package for package in packages if package.package_type == "pypi"
    ]
    if len(pypi_packages) > 0:
        subprocess.run(
            f"pixi add {_stringify_packages(pypi_packages)} --pypi",
            shell=True,
            check=True,
        )

    print(f"Installed {num_packages} packages.")


def remove(packages: List[PythonPackageDependency]):
    num_packages: int = len(packages)
    if num_packages == 0:
        print("No packages to remove")
        return

    pre_run()

    # Uninstall / Remove the packages
    print("Removing packages...")

    # Remove the non-pypi packages
    conda_packages: List[PythonPackageDependency] = [
        package for package in packages if package.package_type == "non-pypi"
    ]
    if len(conda_packages) > 0:
        subprocess.run(
            f"pixi remove {_stringify_packages(conda_packages, include_versions=False)} --no-install",
            shell=True,
            check=True,
        )

    # Remove the pypi packages
    pypi_packages: List[PythonPackageDependency] = [
        package for package in packages if package.package_type == "pypi"
    ]
    if len(pypi_packages) > 0:
        subprocess.run(
            f"pixi remove {_stringify_packages(pypi_packages, include_versions=False)} --no-install --pypi",
            shell=True,
            check=True,
        )

    print(f"Removed {num_packages} packages.")

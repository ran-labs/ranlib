from typing import List, Dict, Set, Union, Tuple
from pydantic import BaseModel, Field

import subprocess

from state.ranstate import PythonPackageDependency, read_ran_toml, RanTOML


def detect_package_manager() -> str:
    ran_toml: RanTOML = read_ran_toml()

    return ran_toml.settings.package_manager


def stringify_packages(packages: List[PythonPackageDependency]) -> str:
    pkgs_str: str = ""
    for package in packages:
        pkgs_str += f"{package.package_name}=={package.version} "

    return pkgs_str


def install(packages: List[PythonPackageDependency], package_manager: str):
    if len(packages) == 0:
        return

    install_cmd: str = ""

    if package_manager == "poetry":
        install_cmd = "add"
    else:
        install_cmd = "install"

    # Run this
    print("Installing Packages...")
    subprocess.run(
        f"{package_manager} {install_cmd} {stringify_packages(packages)}", shell=True
    )


def remove(
    packages: List[PythonPackageDependency], package_manager: str, lenient: bool = False
):
    remove_cmd: str = ""

    if package_manager in {"poetry", "conda", "mamba", "micromamba"}:
        remove_cmd = "remove"
    else:
        remove_cmd = "uninstall"

    for package in packages:
        if lenient is False or (
            package.isolated or package_manager in {"poetry", "pipenv"}
        ):
            # Uninstall / Remove the package
            subprocess.run(f"{package_manager} {remove_cmd} {package.package_name}")

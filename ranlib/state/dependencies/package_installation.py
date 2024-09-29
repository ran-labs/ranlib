import subprocess
from typing import Union

from ranlib.constants import DEPENDENCIES_NAMES
from ranlib.state.ranstate import PythonPackageDependency, RanTOML, read_ran_toml

# TODO: Enforce isolation


def _stringify_packages(
    packages: list[PythonPackageDependency],
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

        if not include_versions:
            package_str = package.package_name
            if package.package_type == "non-pypi":
                package_str = package.channel + package_str

        pkgs_str += package_str + separator

    return pkgs_str


def _ignore_ranlib_dependencies(
    packages: list[PythonPackageDependency],
) -> list[PythonPackageDependency]:
    return [package for package in packages if package.package_name not in DEPENDENCIES_NAMES]


def install(packages: list[PythonPackageDependency]):
    pkgs: list[PythonPackageDependency] = _ignore_ranlib_dependencies(packages)
    num_packages: int = len(pkgs)
    if num_packages == 0:
        print("No packages to install.")
        return

    # Install the packages
    print("Installing Packages...")

    # Install the non-pypi packages
    conda_packages: list[PythonPackageDependency] = [
        package for package in pkgs if package.package_type == "non-pypi"
    ]
    if len(conda_packages) > 0:
        try:
            subprocess.run(
                f"pixi add {_stringify_packages(conda_packages)}",
                shell=True,
                check=True,
            )
        except:
            print("Couldn't use exact conda package versions. Trying approximate ones...")
            subprocess.run(
                f"pixi add {_stringify_packages(conda_packages, include_versions=False)}",
                shell=True,
                check=True,
            )

    # Install the pypi packages
    pypi_packages: list[PythonPackageDependency] = [
        package for package in pkgs if package.package_type == "pypi"
    ]
    if len(pypi_packages) > 0:
        try:
            subprocess.run(
                f"pixi add {_stringify_packages(pypi_packages)} --pypi",
                shell=True,
                check=True,
            )
        except:
            print("Couldn't use exact pypi package versions. Trying approximate ones...")
            subprocess.run(
                f"pixi add {_stringify_packages(pypi_packages, include_versions=False)} --pypi",
                shell=True,
                check=True,
            )

    print(f"Installed {num_packages} packages.")


def remove(packages: list[PythonPackageDependency]):
    pkgs: list[PythonPackageDependency] = _ignore_ranlib_dependencies(packages)
    num_packages: int = len(pkgs)
    if num_packages == 0:
        print("No packages to remove")
        return

    # Uninstall / Remove the packages
    print("Removing packages...")

    # Remove the non-pypi packages
    conda_packages: list[PythonPackageDependency] = [
        package for package in pkgs if package.package_type == "non-pypi"
    ]
    if len(conda_packages) > 0:
        subprocess.run(
            f"pixi remove {_stringify_packages(conda_packages, include_versions=False)} --no-install",
            shell=True,
            check=True,
        )

    # Remove the pypi packages
    pypi_packages: list[PythonPackageDependency] = [
        package for package in pkgs if package.package_type == "pypi"
    ]
    if len(pypi_packages) > 0:
        subprocess.run(
            f"pixi remove {_stringify_packages(pypi_packages, include_versions=False)} --no-install --pypi",
            shell=True,
            check=True,
        )

    print(f"Removed {num_packages} packages.")

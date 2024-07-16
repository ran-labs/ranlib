from typing import List, Dict, Set, Union, Tuple
from pydantic import BaseModel, Field

from ranlib.state.ranstate import RanPaperInstallation, PythonPackageDependency

from packaging.version import parse


def preresolve_dependencies(
    dependencies: List[RanPaperInstallation],
) -> List[PythonPackageDependency]:
    all_dependencies: List[PythonPackageDependency] = []
    for dependency in dependencies:
        all_dependencies += dependency.package_dependencies

    # Pre-resolution

    # Remove duplicates
    pypackage_deps: List[PythonPackageDependency] = list(set(all_dependencies))
    preresolved_dependencies: List[PythonPackageDependency] = []

    def package_name_added(name: str) -> int:
        for i, package in enumerate(preresolved_dependencies):
            if package.package_name == name:
                return i

        return -1

    for package in pypackage_deps:
        pkg_idx: int = package_name_added(package.package_name)
        pkg_name_added: bool = pkg_idx != -1

        # Check if the package's name was already added to preresolved_dependencies
        if pkg_name_added:
            existing_pkg: PythonPackageDependency = preresolved_dependencies[pkg_idx]

            # First, prioritize the isolated ones
            if package.isolated != existing_pkg.isolated:
                if package.isolated:
                    # Copy the dominant properties
                    existing_pkg.isolated = True
                    existing_pkg.version = package.version  # potential bug here
                    # the package names are already the same, so no need to change that
                    existing_pkg.package_type = package.package_type
                    existing_pkg.channel = package.channel
            else:
                # Otherwise, prioritize the lower versions

                # Find which package has the lowest version
                if parse(package.version.lower_bound) < parse(existing_pkg.version.lower_bound):
                    # If the existing package has the lowest version, then use that
                    existing_pkg.version = package.version
                    existing_pkg.package_type = package.package_type
                    existing_pkg.channel = package.channel
        else:
            # If not already added, then add
            preresolved_dependencies.append(package)

    return preresolved_dependencies


def resolve_to_deltas(
    pkg_deps_new: List[PythonPackageDependency],
    pkg_deps_old: List[PythonPackageDependency],
) -> Tuple[List[PythonPackageDependency], List[PythonPackageDependency]]:
    """
    Returns a tuple of (to_add, to_remove)
    """
    pkg_deps_new_set: Set[PythonPackageDependency] = frozenset(pkg_deps_new)
    pkg_deps_old_set: Set[PythonPackageDependency] = frozenset(pkg_deps_old)

    to_add_packages: List[PythonPackageDependency] = list(
        pkg_deps_new_set - pkg_deps_old_set
    )
    to_remove_packages: List[PythonPackageDependency] = list(
        pkg_deps_old_set - pkg_deps_new_set
    )

    return (to_add_packages, to_remove_packages)

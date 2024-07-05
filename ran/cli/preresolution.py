from typing import List, Dict, Set, Union, Tuple
from pydantic import BaseModel, Field

from state import RanPaperInstallation, PythonPackageDependency


# TODO:
def preresolve_dependencies(
    dependencies: List[RanPaperInstallation],
) -> List[PythonPackageDependency]:
    pass


def resolve_to_deltas(
    pkg_deps_new: List[PythonPackageDependency],
    pkg_deps_old: List[PythonPackageDependency],
) -> Tuple[List[PythonPackageDependency], List[PythonPackageDependency]]:
    """
    Returns a tuple of (to_add, to_remove)
    """
    pass

from typing import List, Dict
from pathlib import Path

import tomli
import re
import textwrap


# Paths
# I didn't want to import from constants. That could cause potential issues on a recursive base case (which is now) due to the way Python's circular imports work
_LIB_ROOT: str = str(Path(__file__).parent)

# Note: this function ONLY works in dev and is hence excluded from the actual library
def _read_dependencies() -> List[str]:
    """
    Read the dependencies of ranlib
    """
    
    with open(f"{_LIB_ROOT}/pyproject.toml", 'rb') as pyproject_dot_toml_file:
        pyproject_dot_toml: Dict = tomli.load(pyproject_dot_toml_file)

    dependencies: List[str] = pyproject_dot_toml["project"]["dependencies"]
    cleaned_dependencies: List[str] = []

    for dependency in dependencies:
        # First, remove all whitespace (normalization)
        _dep_: str = re.sub(r"\s+", "", dependency)
        
        clean_dep: str = _dep_[:min(_dep_.index(">"), _dep_.index("<"))]
        cleaned_dependencies.append(clean_dep)

    return cleaned_dependencies


if __name__ == "__main__":
    # Read Project Dependencies
    DEPENDENCIES_NAMES: List[str] = _read_dependencies()

    # Write them to that python file (./ranlib/generated/dependencies.py)
    with open(f"{_LIB_ROOT}/ranlib/generated/dependencies.py", 'w') as dependencies_dot_py_file:
        dependencies_dot_py_file.write(
            textwrap.dedent(f"""
            ## GENERATED CODE ##
            ## DO NOT MODIFY DIRECTLY ##

            from typing import List


            DEPENDENCIES_NAMES: List[str] = {str(DEPENDENCIES_NAMES)}
            """).strip()
        )


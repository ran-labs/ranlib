from pathlib import Path

import tomli
import re
import textwrap
import subprocess


# Paths
# I didn't want to import from constants. That could cause potential issues on a recursive base case (which is now) due to the way Python's circular imports work
_PROJECT_ROOT: str = str(Path(__file__).parent)

# Note: this function ONLY works in dev and is hence excluded from the actual library
def _read_dependencies() -> list[str]:
    """
    Read the dependencies of ranlib
    """
    
    with open(f"{_PROJECT_ROOT}/pyproject.toml", 'rb') as pyproject_dot_toml_file:
        pyproject_dot_toml: dict = tomli.load(pyproject_dot_toml_file)

    dependencies: list[str] = pyproject_dot_toml["project"]["dependencies"]
    cleaned_dependencies: list[str] = []

    for dependency in dependencies:
        # First, remove all whitespace (normalization)
        _dep_: str = re.sub(r"\s+", "", dependency)
        
        clean_dep: str = _dep_[:min(_dep_.index(">"), _dep_.index("<"))]
        cleaned_dependencies.append(clean_dep)

    return cleaned_dependencies


if __name__ == "__main__":
    # Read Project Dependencies
    DEPENDENCIES_NAMES: list[str] = _read_dependencies()

    # Write them to that python file (./ranlib/_generated/lib_dependencies.py)
    with open(f"{_PROJECT_ROOT}/ranlib/_generated/lib_dependencies.py", 'w') as lib_dependencies_dot_py_file:
        lib_dependencies_dot_py_file.write(
            textwrap.dedent(f"""
            ## GENERATED CODE ##
            ## DO NOT MODIFY DIRECTLY ##

            DEPENDENCIES_NAMES: list[str] = {str(DEPENDENCIES_NAMES)}
            """).strip()
        )
    
    # Rewrite the installation every time it builds
    subprocess.run(
        "bashify installation/install_template.sh --out installation/_out/install.sh",
        shell=True,
        check=True
    )

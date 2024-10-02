import functools
import os
import subprocess
from typing import Callable

from ranlib._external.install_checks import ensure_pixi_installation
from ranlib.state.pathutils import (
    add_root_path,
    environment_yml_exists,
    find_root_path,
    pixi_project_exists,
    set_root_path,
)


def pre(fns: list[Callable]):
    """
    Stuff that executes before the function. For improved code readability and composability
    However, they cannot have arguments, so if you want to use args, you'll have to settle with lambdas
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute all functions before a command first
            for fn in fns:
                fn()

            # Execute the actual function
            result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator


def manifest_project_root():
    """Manifest the User Project Root before every single command."""

    root_path: str = find_root_path()

    if root_path is None:
        root_path = os.getcwd()
        add_root_path(root_path)

    set_root_path(root_path)


def manifest_pixi_project():
    # First, check if pixi is installed or not. If not, then install it
    ensure_pixi_installation()

    # If pixi project not initialized, then do this
    if not pixi_project_exists():
        _init_pixi_project_raw()


# Do not call anywhere but from this file
def _init_pixi_project_raw():
    # Initialize a pixi project
    root_path: str = (
        find_root_path()
    )  # if this is None, then that means that manifest_project_root wasn't called before
    init_cmd: str = f"pixi init {root_path}"

    environment_yml: str | bool = environment_yml_exists(return_which=True)
    if environment_yml:
        print(
            "Conda project detected. Converting to Pixi...(don't worry it's better and easier to use with more functionality)"
        )
        init_cmd += f" --import {root_path}/{environment_yml}"

    subprocess.run(init_cmd, shell=True, check=True)

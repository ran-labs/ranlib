import os
from typing import List, Callable

import functools
import subprocess

from ranlib.state.pathutils import find_root_path, set_root_path, add_root_path
from ranlib._external.install_checks import check_pixi_installation



def pre(fns: List[Callable]):
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
    check_pixi_installation()

    # If pixi project not initialized (no pixi.toml), then do this
    root_path: str = find_root_path()
    if not os.path.exists(f"{root_path}/pixi.toml"):
        _init_pixi_project_raw()


# This is usually not due to CLI, so I didn't add the autocompletion hooks
def init_pixi_project():
    try:
        subprocess.run("pixi --version", shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Pixi is not installed. Installing pixi...")

        # Install pixi
        subprocess.run(
            "curl -fsSL https://pixi.sh/install.sh | bash", shell=True, check=True
        )

        _init_pixi_project_raw()


def _init_pixi_project_raw():
    # Initialize a pixi project
    init_cmd: str = "pixi init"
    root_path: str = find_root_path()
    if os.path.exists(f"{root_path}/environment.yml"):
        print(
            "Conda project detected. Converting to Pixi...(don't worry it's better and easier to use with more functionality)"
        )
        init_cmd += f" --import {root_path}/environment.yml"

    subprocess.run(init_cmd, shell=True, check=True)

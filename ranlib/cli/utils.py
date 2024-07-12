import os
from pathlib import Path

import functools

from state.pathutils import find_root_path, set_root_path, add_root_path

import subprocess


def manifest_project_root(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Manifest the User Project Root before every single command."""
        root_path: str = find_root_path()

        if root_path is None:
            root_path = os.getcwd()
            add_root_path(root_path)

        set_root_path(root_path)

        # Execute the actual function
        result = func(*args, **kwargs)

        return result

    return wrapper


def check_pixi_installation(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Check if pixi is installed and install it if not."""
        try:
            subprocess.run("pixi --version", shell=True, check=True)
        except subprocess.CalledProcessError:
            print("Pixi is not installed. Installing pixi...")

            # Install pixi
            subprocess.run(
                "curl -fsSL https://pixi.sh/install.sh | bash", shell=True, check=True
            )

            # Also installs the autocompletion for the respective shell
            # Maybe remove this if it becomes a problem
            subprocess.run(
                'eval "$(pixi completion --shell bash)"', shell=True, check=True
            )
            subprocess.run(
                'eval "$(pixi completion --shell zsh)"', shell=True, check=True
            )
            subprocess.run(
                'eval "$(pixi completion --shell fish | source)"',
                shell=True,
                check=True,
            )
            subprocess.run(
                'eval "$(pixi completion --shell elvish | slurp)"',
                shell=True,
                check=True,
            )

            _init_pixi_project_raw()
        # Execute the actual function
        result = func(*args, **kwargs)

        return result


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


def append_to_gitignore(item, gitignore_path=".gitignore"):
    """
    Appends a given item to the .gitignore file.

    Parameters:
    - item (str): The item to add to the .gitignore file.
    - gitignore_path (str): The path to the .gitignore file. Defaults to '.gitignore'.

    Returns:
    - None
    """
    path = Path(gitignore_path)

    # Ensure the .gitignore file exists
    if not path.exists():
        print(f"The file {gitignore_path} does not exist. Creating a new one.")
        path.touch()

    # Read the current contents of the .gitignore file
    with path.open("a") as file:
        file.write(f"\n{item}\n")

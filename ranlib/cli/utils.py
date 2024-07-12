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
            subprocess.run("curl -fsSL https://pixi.sh/install.sh | bash", shell=True, check=True)
            
            # Also installs the autocompletion for the respective shell
            # Maybe remove this if it becomes a problem
            subprocess.run("eval \"$(pixi completion --shell bash)\"", shell=True, check=True)
            subprocess.run("eval \"$(pixi completion --shell zsh)\"", shell=True, check=True)
            subprocess.run("eval \"$(pixi completion --shell fish | source)\"", shell=True, check=True)
            subprocess.run("eval \"$(pixi completion --shell elvish | slurp)\"", shell=True, check=True)

        try:
            subprocess.run("pixi --version", shell=True, check=True)
        except subprocess.CalledProcessError:
            print("Pixi is not installed. Installing it now...")
            subprocess.run("pip install pixi", shell=True, check=True)

        # Execute the actual function
        result = func(*args, **kwargs)

        return result


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

import os
from pathlib import Path

import functools

from state.pathutils import find_root_path, set_root_path, add_root_path


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

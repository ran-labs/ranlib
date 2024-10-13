import os
import re
import socket
from pathlib import Path


def delete_all_files_glob(directory: str, pattern: str):
    path = Path(directory)
    for file in path.glob(pattern):
        file.unlink()


def find_all_python_files(directory: str) -> list[str]:
    """
    Recursively finds all Python files in the given directory and its subdirectories.

    :param directory: Path to the directory to start searching from.
    :return: List of paths to all Python files found.
    """
    python_files: list[str] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def append_to_gitignore(item: str, gitignore_path: str = ".gitignore"):
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


def remove_all_whitespace(s: str) -> str:
    return re.sub(r"\s+", "", s)


def find_open_localhost_port() -> int:
    # Top 50 candidates. Being lazy here
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0

    first_candidates: list[int] = [
        5000,
        8000,
        8080,
        8787,
        9001,
        4321,
    ]

    for candidate in first_candidates:
        if is_port_open(candidate):
            return candidate

    remaining: int = 50 - len(first_candidates)
    backup_candidates: list[int] = [(5001 + i) for i in range(remaining)]

    for candidate in backup_candidates:
        if is_port_open(candidate):
            return candidate

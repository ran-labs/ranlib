import os
import re
from pathlib import Path
from typing import List


def delete_all_files_glob(directory: str, pattern: str):
    path = Path(directory)
    for file in path.glob(pattern):
        file.unlink()


def find_all_python_files(directory: str) -> List[str]:
    """
    Recursively finds all Python files in the given directory and its subdirectories.

    :param directory: Path to the directory to start searching from.
    :return: List of paths to all Python files found.
    """
    python_files: List[str] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def remove_all_whitespace(s: str) -> str:
    return re.sub(r"\s+", "", s)

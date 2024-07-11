import os
import sys

from state.pathutils import get_dotran_dir_path
from constants import DOTRAN_FOLDER_NAME

from __init__ import __version__


# -- .ran/ --
def generate_dotran_dir():
    dotran_dir_path: str = get_dotran_dir_path()

    # Generate .ran/ directory and .ran/ran_modules directory
    try:
        os.makedirs(dotran_dir_path, exist_ok=True)
        print(f"Directory '{DOTRAN_FOLDER_NAME}/' created successfully.")

        # os.makedirs(f"{dotran_dir_path}/{RAN_MODULES_FOLDER_NAME}", exist_ok=True)
        # print(f"Directory '{DOTRAN_FOLDER_NAME}/' created successfully.")

        # This way, we can do from ran import <paper_id>
        # sys.path.append(dotran_dir_path)
    except OSError as error:
        print(
            f"Directory '{DOTRAN_FOLDER_NAME}/' cannot be created successfully. Error: {error}"
        )

    # Generate a RANFILE (.ran/ran_modules/RANFILE) [lightweight lil file that doesnt do much]
    with open(f"{dotran_dir_path}/RANFILE", "w") as ranfile:
        ranfile.write(f"RANLIB Version {__version__}")

    # Generate __init__.py
    with open(f"{dotran_dir_path}/__init__.py", "w") as hackyworkaroundfile:
        hackyworkaroundfile.write("from ranlib import *")

import os

from ranlib.constants import DOTRAN_FOLDER_NAME

# import sys
from ranlib.state.pathutils import get_dotran_dir_path
from ranlib.state.ranfile import RANFILE


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
        print(f"Directory '{DOTRAN_FOLDER_NAME}/' cannot be created successfully. Error: {error}")

    # Generate a RANFILE (ran/RANFILE) [lightweight lil file]
    RANFILE().write_to_ranfile()

    # Generate __init__.py
    with open(f"{dotran_dir_path}/__init__.py", "w") as hackyworkaroundfile:
        hackyworkaroundfile.write("from ranlib import *")

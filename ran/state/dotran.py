import os

from state.pathutils import get_dotran_dir_path
from __init__ import __version__


# -- .ran/ --
def generate_dotran_dir():
    dotran_dir_path: str = get_dotran_dir_path()

    # Generate .ran/ directory and .ran/ran_modules directory
    try:
        os.makedirs(dotran_dir_path, exist_ok=True)
        print("Directory '.ran/' created successfully.")

        os.makedirs(f"{dotran_dir_path}/ran_modules", exist_ok=True)
        print("Directory '.ran/ran_modules' created successfully.")
    except OSError as error:
        print(f"Directory '.ran/' cannot be created successfully. Error: {error}")

    # Generate a RANFILE (.ran/ran_modules/RANFILE) [lightweight lil file that doesnt do much]
    with open(f"{dotran_dir_path}/ran_modules/RANFILE", "w") as ranfile:
        ranfile.write(f"RANLIB Version {__version__}")

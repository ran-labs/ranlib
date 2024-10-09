from pathlib import Path

from ranlib._generated.lib_dependencies import DEPENDENCIES_NAMES

# Paths
PROJECT_ROOT: str = str(Path(__file__).parent.parent)

# Naming conventions
DOTRAN_FOLDER_NAME: str = "ran"  # Used to be .ran
# RAN_MODULES_FOLDER_NAME: str = (
#     "."  # This is for the relative paths  # Used to be "ran_modules"
# )
PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME: str = "_lib"

# Project Constants
DEFAULT_ISOLATION_VALUE: bool = False
RAN_DEFAULT_AUTHOR_NAME: str = "#randefault"  # '#' tends to be a macro for certain actions

RAN_API_SERVER_URL: str = "https://lib.ran.so"

RAN_AUTH_TOKEN_FILEPATH_JSON: str = "~/ran/.ranprofile.json"

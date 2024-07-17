from pathlib import Path


# Paths
LIB_ROOT: str = str(Path(__file__).parent.parent)

# Naming conventions
DOTRAN_FOLDER_NAME: str = "ran"  # Used to be .ran/
# RAN_MODULES_FOLDER_NAME: str = (
#     "."  # This is for the relative paths  # Used to be "ran_modules"
# )
PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME: str = "_lib"

# Project Constants
DEFAULT_ISOLATION_VALUE: bool = False
RAN_DEFAULT_AUTHOR_NAME: str = "randefault"

RAN_REGISTRY_GIT_HTTPS_URL: str = "https://github.com/anemo-ai/ran-registry.git"
RAN_API_SERVER_URL: str = ""  # TODO: put something here

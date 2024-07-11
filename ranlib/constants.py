from pathlib import Path


# Paths
LIB_ROOT: str = str(Path(__file__).parent.parent)

# Naming conventions
PAPER_IMPLEMENTATIONS_BODY_FOLDER_NAME: str = "_lib"
RAN_MODULES_FOLDER_NAME: str = "ran"  # Used to be "ran_modules"

# Project Constants
DEFAULT_ISOLATION_VALUE: bool = False
RAN_DEFAULT_AUTHOR_NAME: str = "randefault"

RAN_REGISTRY_GIT_HTTPS_URL: str = "https://github.com/anemo-ai/ran-registry.git"

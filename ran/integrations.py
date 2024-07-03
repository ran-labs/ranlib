from enum import Enum


class Integration(str, Enum):
    AUTO = "auto"
    NONE = "none"
    GIT = "git"
    GITHUB = "github"
    GITLAB = "gitlab"

    # Alias for git
    HUGGINGFACE = "huggingface"

    # Alias for github
    DAGSHUB = "dagshub"


# Assumes integration is AUTO
def auto_detect_integration() -> Integration:
    # TODO: Auto detect git repo

    return Integration.NONE

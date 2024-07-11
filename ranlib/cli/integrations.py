from typing import List, Set, Union
from enum import Enum

from git import Repo

from cli.utils import append_to_gitignore


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
    # Auto detect git repo
    try:
        # Try creating a repo object
        repo = Repo(".")

        # If successful, you know it's a git repo
        return Integration.GIT
    except Exception:
        # Not in a git repo
        pass

    return Integration.NONE


def setup_integration(integration: Integration):
    # For auto integration
    # if git repo detected with auto integration, integration is set to git
    if integration == "auto":
        integration = auto_detect_integration()

    # Setup github or gitlab integration for ran (register to RAN registry)
    GIT_INTEGRATONS: Set[str] = {"git", "huggingface"}
    GITHUB_INTEGRATIONS: Set[str] = {"github", "dagshub"}

    if (
        integration in GIT_INTEGRATONS
        or integration in GITHUB_INTEGRATIONS
        or integration == Integration.GITLAB
    ):
        # Just make a .ran/.gitignore and put the ran_modules/ directory in there
        # append_to_gitignore(".ran/ran_modules/", gitignore_path=".gitignore")
        # TODO: append necessary stuff to the gitignore
        pass

    # Exclusives
    if integration in GIT_INTEGRATONS:
        # TODO:
        # maybe also do some pre-commit stuff like compilation?
        print("git integration")
    elif integration in GITHUB_INTEGRATIONS:
        # TODO: github CI compilation pipeline
        print("github integration")
    elif integration == "gitlab":
        # TODO: gitlab CI compilation pipeline
        print("gitlab integration")

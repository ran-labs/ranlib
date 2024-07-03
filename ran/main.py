from typing import List, Dict, Union, Set

import typer

import state
from cli import initialization as init
from integrations import Integration, auto_detect_integration


app = typer.Typer()


# ran setup
@app.command()
def setup(integration: Integration = "auto", override: bool = False):
    """
    Setup the project:
        - `ran setup --override` says fuck it and does a full initialization, overriding anything else that existed before
        - Otherwise, run a smart init (reflect each of these options in the logs)
          - if lockfile, init from there
          - else if ran.toml, init from there
          - else, do a full initialization
    """

    if override:
        init.full_init_from_scratch()
    else:
        init.smart_init()

    # For auto integration
    # if git repo detected with auto integration, integration is set to git
    if integration == "auto":
        integration = auto_detect_integration()

    # Setup github or gitlab integration for ran (register to RAN registry)
    GIT_INTEGRATONS: Set[str] = {"git", "huggingface"}
    GITHUB_INTEGRATIONS: Set[str] = {"github", "dagshub"}

    # TODO:
    if integration in GIT_INTEGRATONS:
        # Just make a .ran/.gitignore and put the ran_modules/ directory in there
        # maybe also do some pre-commit stuff like compilation?
        pass
    elif integration in GITHUB_INTEGRATIONS:
        pass
    elif integration == "gitlab":
        pass


# ran install
@app.command()
def install(from_rantoml: bool = False):
    """Installs the papers from the lockfile, unless the user specifies to be from ran.toml. If lockfile not found, try ran.toml"""
    if from_rantoml:
        init.init_from_rantoml()
    else:
        init.smart_init(allow_init_from_scratch=False)


# TODO:
# ran use
@app.command()
def use(paper_impl_id: List[str]):
    """Installs a paper library/module (or multiple)"""
    # Fetch from DB
    # git clone it & remove everything that doesnt really matter
    # Pre-Resolve and Install the dependencies of the paper
    # Compile if needed into .ran/ran_modules
    # Add it to ran.toml dependencies
    # Generate/Update lockfile
    pass


# TODO:
# ran remove
@app.command()
def remove(paper_impl_id: List[str]):
    """Removes a paper installation (or multiple)"""
    # Remove modules from .ran/ran_modules
    # Remove its entry in ran.toml
    # Generate/Update lockfile
    pass


# ran savestate
@app.command()
def savestate():
    state.generate_lockfile()


# ran lock
@app.command()
def lock():
    state.generate_lockfile()


# ran loadstate
@app.command()
def loadstate():
    """Load from the lockfile that is in .ran/ran-lock.json"""
    init.init_from_lockfile()


# TODO:
# ran push
@app.command()
def push():
    """
    Optionally compile the code and push to the specified remote.
    What IS required though is that a compilation graph/dump is produced and written to a file, so that a user can easily recompile on their own machine
    When this project is setup with git / github / gitlab integrations, this will run on pushing to those
    """
    pass


# Start Typer CLI
if __name__ == "__main__":
    app()

from typing import List, Dict, Union, Set

import typer

import state
from cli import initialization as init
from integrations import Integration, setup_integration


app = typer.Typer()


# TODO: ran setup --papers paper1 paper2 paper3
# TODO: `ran use paper1` will also do a `ran setup` before doing it if the setup has not happened yet


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

    # Setup the integration
    if integration != "none":
        setup_integration(integration)


# ran install
@app.command()
def install(from_rantoml: bool = False):
    """Installs the papers from the lockfile, unless the user specifies to be from ran.toml. If lockfile not found, try ran.toml"""
    if from_rantoml:
        init.init_from_ran_toml()
    else:
        init.smart_init(allow_init_from_scratch=False)


# TODO:
# ran use
@app.command()
def use(paper_impl_id: List[str], isolated: bool = False):
    """Installs a paper library/module (or multiple)"""
    # DW ABT THIS RN

    # 1.) Produce lock (pre-resolve packages if needed)
    # 2.) (Clone + Compile/Transpile if needed), Package installation
    # 3.) Update ran.toml dependencies and lockfile

    # Fetch git urls from DB
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
    # For any isolated packages associated with the module(s), remove 'em
    # Generate/Update lockfile
    pass


# ran loadstate
@app.command()
def loadstate():
    """Load from the lockfile that is in .ran/ran-lock.json"""
    init.init_from_lockfile()


# TODO:
# ran push
@app.command()
def push(compile: bool = False):
    """
    Optionally compile the code and push to the specified remote.
    What IS required though is that a compilation tree/dump is produced and written to a file, so that a user can easily recompile on their own machine
    When this project is setup with git / github / gitlab integrations, this will run on pushing to those
    """
    # 1.) Optionally compile
    # 2.) Update lockfile
    # 3.) git push
    pass


# TODO:
# ran help
@app.command()
def help():
    """ran help"""
    pass


# Start Typer CLI
if __name__ == "__main__":
    app()

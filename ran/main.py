import os
import sys

from typing import List, Dict, Union, Set

import typer

from state.ranstate import PaperImplID, RanTOML, RanLock, read_ran_toml
from cli import initialization as init
from cli import modify_papers
from cli.utils import manifest_project_root
from cli.integrations import Integration, setup_integration

from constants import DEFAULT_ISOLATION_VALUE


app = typer.Typer()


# os.chdir(".ran/ran_modules")
# sys.path.append(os.path.join(os.getcwd()))
# from ran import mamba


# ran setup
@app.command()
@manifest_project_root
def setup(
    papers: List[str] = [],
    isolated: bool = DEFAULT_ISOLATION_VALUE,
    integration: Integration = "auto",
    override: bool = False,
):
    """
    Setup the project:
        - `ran setup --override` says fuck it and does a full initialization, overriding anything else that existed before
        - Otherwise, run a smart init (reflect each of these options in the logs)
          - if lockfile, init from there
          - else if ran.toml, init from there
          - else, do a full initialization
    """
    # TODO: ran setup github should not reinitialize the project

    if override:
        init.full_init_from_scratch()
    else:
        init.smart_init()

    # Setup the integration
    if integration != "none":
        setup_integration(integration)

    # Make the isolated value change the default isolation value on the ran.toml
    ran_toml: RanTOML = read_ran_toml()
    ran_toml.settings.isolate_dependencies = isolated

    # Setup the papers
    if len(papers) > 0:
        modify_papers.add_papers(papers, isolated)


# ran install
@app.command()
@manifest_project_root
def install(from_rantoml: bool = False):
    """Installs the papers from the lockfile, unless the user specifies to be from ran.toml. If lockfile not found, try ran.toml"""
    # This will ALWAYS fresh install

    if from_rantoml:
        init.init_from_ran_toml()
        return

    init.smart_init(allow_init_from_scratch=False)


# ran update
@app.command()
@manifest_project_root
def update():
    """Installs from the ran.toml file. In case the user wants to use this. This will NOT fresh install everything unless there is no lockfile"""
    init.init_from_ran_toml(force_fresh_install=False)


# ran loadstate
@app.command()
@manifest_project_root
def loadstate():
    """Load from the lockfile that is in .ran/ran-lock.json"""
    # init_from_lockfile will always be from zero since otherwise nothing would happpen (x - x = 0, but x - 0 = x)
    init.init_from_lockfile()


# ran use
@app.command()
@manifest_project_root
def use(paper_impl_ids: List[str], isolated: bool = False):
    """Installs a paper library/module (or multiple), updates the lockfile, then updates ran.toml"""

    if not init.appears_to_be_initialized():
        print("RAN does not appear to be initialized. Initializing first...")
        init.smart_init()

    # Convert papers to PaperImplID
    paper_implementation_ids: List[PaperImplID] = [
        PaperImplID.from_str(paper_impl_id) for paper_impl_id in paper_impl_ids
    ]

    # Add them
    modify_papers.add_papers(paper_implementation_ids, isolated)


# ran remove
@app.command()
@manifest_project_root
def remove(paper_impl_ids: List[str]):
    """Removes a paper installation (or multiple), updates the lockfile, then updates ran.toml"""
    # Remove modules from .ran/ran_modules
    # Remove its entry in ran.toml
    # For any isolated packages associated with the module(s), remove 'em
    # Generate/Update lockfile

    # Convert papers to PaperImplID
    paper_implementation_ids: List[PaperImplID] = [
        PaperImplID.from_str(paper_impl_id) for paper_impl_id in paper_impl_ids
    ]

    # Remove them
    modify_papers.remove_papers(paper_implementation_ids)


# NOTE: this is not needed unless we have our own repo hosting system
# As of right now, git push should auto-push to ran if need-be
# ran push
# @app.command()
# @manifest_project_root
# def push(compile: bool = False):
#     """
#     Optionally compile the code and push to the specified remote.
#     What IS required though is that a compilation tree/dump is produced and written to a file, so that a user can easily recompile on their own machine
#     When this project is setup with git / github / gitlab integrations, this will run on pushing to those
#     """
#     # 1.) Optionally compile (for now, not needed on push)
#     # 2.) Update lockfile for compilation steps if compile
#     # 3.) git push
#     pass


# TODO:
# ran help
@app.command()
def help():
    """Print all the help commands"""
    pass


# Start Typer CLI
if __name__ == "__main__":
    app()

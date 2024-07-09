from typing import List, Dict, Union, Set

import typer
import os
import sys

from state.ranstate import PaperImplID, RanTOML, RanLock
from cli import initialization as init
from cli import modify_papers
from cli.integrations import Integration, setup_integration

from constants import DEFAULT_ISOLATION_VALUE


app = typer.Typer()
# print(os.getcwd())
# print(sys.path)
# os.chdir("/home/sanner/Coding/Work/Anemo/ranlib/ran/.ran")
# print(os.getcwd())
# print(os.listdir('.'))
# print(sys.path)
# sys.path.append(os.getcwd())
# from ran_modules import mamba

print(os.getcwd())
# print(os.listdir('.'))
os.chdir("ran/")

# print(os.listdir('.'))
os.chdir(".ran/ran_modules/")
# print(os.listdir('.'))
sys.path.append(os.path.join(os.getcwd()))

# print(sys.path)
from ran import mamba
mamba.greet()


# ran setup
@app.command()
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

    if override:
        init.full_init_from_scratch()
    else:
        init.smart_init()

    # Setup the integration
    if integration != "none":
        setup_integration(integration)

    # Setup the papers
    if len(papers) > 0:
        modify_papers.add_papers(papers, isolated)


# ran install
@app.command()
def install(from_rantoml: bool = False):
    """Installs the papers from the lockfile, unless the user specifies to be from ran.toml. If lockfile not found, try ran.toml"""
    if from_rantoml:
        init.init_from_ran_toml()
    else:
        init.smart_init(allow_init_from_scratch=False)


# ran use
@app.command()
def use(paper_impl_ids: List[str], isolated: bool = False):
    """Installs a paper library/module (or multiple), updates the lockfile, then updates ran.toml"""

    if not init.appears_to_be_initialized():
        print("RAN appears not to be initialized. Initializing first...")
        init.smart_init()

    # Convert papers to PaperImplID
    paper_implementation_ids: List[PaperImplID] = [
        PaperImplID.from_str(paper_impl_id) for paper_impl_id in paper_impl_ids
    ]

    # Add them
    modify_papers.add_papers(paper_implementation_ids, isolated)


# ran remove
@app.command()
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

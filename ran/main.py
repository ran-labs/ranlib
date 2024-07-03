from typing import List, Dict, Any, Optional, Union

import typer
import constants


app = typer.Typer()


# ran setup
@app.command()
def setup(integration: str = "none", override: bool = False):
    """Integration can either be github or gitlab"""
    # If not already setup, setup project in current directory
    if not constants.IS_SETUP:
        # setup project in current directory
        pass

        # Use existing (if there exists one) by default, unless override is True

        # if there does not exist one, or if override is True, do a full initialization

        # By the end of this portion, there should be a .ran/ directory and a ran.toml file

    # Setup github or gitlab integration for ran (register to RAN registry)
    if integration == "github":
        pass
    elif integration == "gitlab":
        pass


# ran install
@app.command()
def install():
    """Installs the papers from the lockfile"""
    pass


# ran use
@app.command()
def use(paper_impl_id: List[str]):
    """Installs a paper library (or multiple)"""
    # Fetch from DB
    # git clone it & remove everything that doesnt really matter
    # Pre-Resolve and Install the dependencies of the paper
    # Compile if needed into .ran/ran_modules
    # Add it to ran.toml dependencies
    # Generate/Update lockfile
    pass


# ran remove
@app.command()
def remove(paper_impl_id: List[str]):
    """Removes a paper installation (or multiple)"""
    # Remove modules from .ran/ran_modules
    # Remove its entry in ran.toml
    # Generate/Update lockfile
    pass


def generate_lockfile():
    """Generate/Update a lockfile for the papers in .ran/ran-lock.json"""
    pass


# ran savestate
@app.command()
def savestate():
    generate_lockfile()


# ran lock
@app.command()
def lock():
    generate_lockfile()


# ran loadstate
@app.command()
def loadstate():
    """Load from the lockfile that is in .ran/ran-lock.json"""
    pass


# ran push
@app.command()
def push():
    """
    Optionally compile the code and push to the specified remote.
    What IS required though is that a compilation graph/dump is produced and written to a file, so that a user can easily recompile on their own machine
    """
    pass


# Start Typer CLI
if __name__ == "__main__":
    app()

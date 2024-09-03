from typing import List, Dict, Union, Set
from typing_extensions import Annotated

import typer
import subprocess

# State
from ranlib.state.ranstate import PaperImplID, RanTOML, RanLock, read_ran_toml
from ranlib.constants import DEFAULT_ISOLATION_VALUE

# Actions
from ranlib.actions import initialization as init
from ranlib.actions import modify_papers, integrations
from ranlib.actions.publish import push_entry

from ranlib.actions.integrations import Integration

# Helpers
from ranlib.cli.helpers import pre, manifest_project_root, manifest_pixi_project

# Subcommands
from ranlib.cli.subcmds import dev, auth


app = typer.Typer(rich_markup_mode="rich")


# ran setup
@app.command(epilog=":rocket: [orange]Skyrocket[/orange] your Research")
@pre([manifest_project_root, manifest_pixi_project])
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
        integrations.setup_integration(integration)

    # Make the isolated value change the default isolation value on the ran.toml
    ran_toml: RanTOML = read_ran_toml()
    ran_toml.settings.isolate_dependencies = isolated

    # Setup the papers
    if len(papers) > 0:
        modify_papers.add_papers(papers, isolated)


@app.command(epilog=":rocket: [orange]Skyrocket[/orange] your Research")
@pre([manifest_project_root])
def integrate(integration: Integration = "auto"):
    """Setup integrations such as git, github, etc."""

    # Setup the integration
    if integration != "none":
        integrations.setup_integration(integration)


# ran install
@app.command(epilog=":rocket: [orange]Skyrocket[/orange] your Research")
@pre([manifest_project_root, manifest_pixi_project])
def install(from_rantoml: bool = False):
    """Installs the papers from the lockfile, unless the user specifies to be from ran.toml. If lockfile not found, try ran.toml"""
    # This will ALWAYS fresh install
    
    if from_rantoml:
        init.init_from_ran_toml()
        raise typer.Exit()  # used to be 'return'

    init.smart_init(allow_init_from_scratch=False)


# ran update
@app.command()
@pre([manifest_project_root, manifest_pixi_project])
def update():
    """
    Installs from the ran.toml file. In case the user wants to use this. This will NOT fresh install everything unless there is no lockfile

    This will sync the lockfile with the ran.toml file (the manifest)
    """
    init.init_from_ran_toml(force_fresh_install=False)


# ran loadstate
@app.command()
@pre([manifest_project_root, manifest_pixi_project])
def loadstate(epilog=":rocket: [orange]Skyrocket[/orange] your Research"):
    """Load from the lockfile that is in ran/ran-lock.json"""
    # init_from_lockfile will always be from zero since otherwise nothing would happpen (x - x = 0, but x - 0 = x)
    init.init_from_lockfile()


# ran use
@app.command()
@pre([manifest_project_root, manifest_pixi_project])
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
@pre([manifest_project_root, manifest_pixi_project])
def remove(paper_impl_ids: List[str]):
    """Removes a paper installation (or multiple), updates the lockfile, then updates ran.toml"""
    # Remove modules from ran/ran_modules
    # Remove its entry in ran.toml
    # For any isolated packages associated with the module(s), remove 'em
    # Generate/Update lockfile
    
    # Convert papers to PaperImplID
    paper_implementation_ids: List[PaperImplID] = [
        PaperImplID.from_str(paper_impl_id) for paper_impl_id in paper_impl_ids
    ]

    # Remove them
    modify_papers.remove_papers(paper_implementation_ids)


# ran push
# As of right now, git push should auto-push to ran if need-be
@app.command()
@pre([manifest_project_root, manifest_pixi_project])
def publish():
    """
    Push to the specified remote.
    What IS required though is that a compilation tree/dump is produced and written to a file, so that a user can easily recompile on their own machine
    When this project is setup with git / github / gitlab integrations, this will run on pushing to those
    """
    push_entry.push_to_registry()


# ran shell
@app.command()
@pre([manifest_pixi_project])
def shell():
    """
    Enters the correct pixi shell (to fix bugs). Really, all this does is run `pixi shell --change-ps1=false`
    """
    # Use the correct pixi shell to avoid errors
    subprocess.run("pixi shell --change-ps1=false", shell=True, check=True)


# TODO: `ran cleanup` for cleaning up pixi installs (like in case the user accidentally runs some ran cmd and it makes a pixi project)


################ SUBCOMMANDS ################
app.add_typer(auth.app, name="auth")
app.add_typer(dev.app, name="dev")


################ START TYPER CLI ################
if __name__ == "__main__":
    app()

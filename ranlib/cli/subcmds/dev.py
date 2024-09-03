"""
This file is for dev commands ONLY for testing in dev
"""

import os

from typing import List, Dict, Union, Set, Optional

import typer

# Helpers
from ranlib.cli.helpers import manifest_project_root, check_pixi_installation


################ IGNORE THE BELOW FOR NOW; DO NOT RELEASE IN PROD ################
app = typer.Typer()


@app.command()
def test():
    """Just stuff to test with as typer is being learned"""
    typer.echo("I just echoed!")

    something: str = typer.prompt("Say something")
    print(f"You just said: {something}")


@app.command()
@manifest_project_root
def reset():
    """ONLY FOR DEBUGGING PURPOSES. DO NOT RELEASE IN PROD"""
    from ranlib.state.pathutils import get_dotran_dir_path, get_ran_toml_path
    import shutil

    shutil.rmtree(get_dotran_dir_path())
    print("Removed ran/")

    os.remove(get_ran_toml_path())
    print("Removed ran.toml")



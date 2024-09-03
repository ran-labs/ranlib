from typing import List, Dict, Union, Optional

import typer

# Helpers
from ranlib.cli.helpers import pre, manifest_project_root, check_pixi_installation


app = typer.Typer()


@app.command()
def login():
    """Log into RAN. Useful for publishing. Or if you want to access private stuff"""
    pass

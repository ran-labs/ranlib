from typing import List, Dict
import typer

# Actions
from ranlib.actions import authentication

# Helpers
from ranlib.cli.helpers import pre, manifest_project_root


app = typer.Typer()


@app.command()
@pre([manifest_project_root])
def login():
    """Log into RAN. Useful for publishing. Or if you want to access private stuff"""
    
    # TODO:
    # 0. Ensure ranx is installed (and pipx by extension). Put this in the pre

    # Check if user is already logged in. If so, ask if they want to log in again
    if authentication.is_user_already_logged_in(verbose=False, debug_mode=False):
        user_response_raw: str = str(typer.prompt("You already seemed to be logged in. Re-log in (for using a different account perhaps)? (Y/n)"))
        login_again: bool = user_response_raw.lower() == "y"
        
        # If yes, then login. Otherwise, terminate the command
        if login_again:
            authentication.execute_login_flow()
    else:
        authentication.execute_login_flow()

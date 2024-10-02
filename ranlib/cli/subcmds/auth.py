import typer

from ranlib._external.install_checks import ensure_ranx_installation

# Actions
from ranlib.actions import authentication

# Helpers
from ranlib.cli.helpers import manifest_project_root, pre

app = typer.Typer()


@app.command()
@pre([manifest_project_root, ensure_ranx_installation])
def login(verbose: bool = False):
    """Log into RAN. Useful for publishing. Or if you want to access private stuff"""

    # Check if user is already logged in. If so, ask if they want to log in again
    if authentication.is_user_already_logged_in(verbose=verbose, debug_mode=False):
        user_response_raw: str = str(
            typer.prompt(
                "You already seemed to be logged in. Re-log in (for using a different account perhaps)? (Y/n)"
            )
        )
        login_again: bool = user_response_raw.lower() == "y"

        # If yes, then login. Otherwise, terminate the command
        if login_again:
            if verbose:
                print("Logging in...")

            authentication.execute_login_flow()
        elif verbose:
            print("Not logging in")
    else:
        authentication.execute_login_flow()

import json
import subprocess
from typing import Optional, Union

import httpx
import typer
from pydantic import BaseModel
from rich import print

from ranlib.constants import RAN_AUTH_TOKEN_FILEPATH_JSON
from ranlib.utils import find_open_localhost_port


class AuthToken(BaseModel):
    token: str


def read_token() -> AuthToken:
    with open(RAN_AUTH_TOKEN_FILEPATH_JSON, 'r') as dot_ranprofile:
        data: dict = json.load(dot_ranprofile)

    auth_token: AuthToken = AuthToken(**data)

    # some small checking just in case
    MIN_TOKEN_LEN: int = 5
    if len(auth_token.token) < MIN_TOKEN_LEN:
        raise Exception("Not a token")

    return auth_token


def is_user_already_logged_in(verbose: bool = False, debug_mode: bool = False) -> bool:
    """
    This function does NOT determine for sure whether the user is completely logged in.
    It just reveals if the user APPEARS to be logged in (as in whether or not they have a token, not whether the token is valid or not), which is enough for the way it is gonna be used in the CLI.
    But point is, don't treat this function like a source of truth
    """
    try:
        with open(RAN_AUTH_TOKEN_FILEPATH_JSON, 'r') as auth_file:
            data: dict = json.load(auth_file)

        auth_creds: AuthToken = AuthToken(**data)

        MIN_TOKEN_LEN: int = 5
        return len(auth_creds.token) >= MIN_TOKEN_LEN
    except Exception as e:
        if verbose or debug_mode:
            print("Unable to read credentials. You are not logged in.")

            if debug_mode:
                print(f"Error: {e}")

        return False


def execute_login_flow():
    """The full login flow"""
    # This assumes ranx is installed
    typer.echo("You'll be logging in through your browser.")

    # Use ranx CLI to take care of the rest
    port: int = find_open_localhost_port()
    subprocess.run(f"ranx open-auth-server --port {port}", shell=True, check=True)

import json
import subprocess
from typing import Optional, Union

import httpx
import typer
from pydantic import BaseModel
from rich import print

from ranlib.constants import RAN_AUTH_TOKEN_FILEPATH_JSON, RAN_API_SERVER_URL
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


def is_token_valid(credentials: AuthToken) -> bool:
    # Check if valid
    try:
        res = httpx.post(
            url=f"{RAN_API_SERVER_URL}/v1/auth/cli/are_credentials_valid",
            headers={"Authorization": f"Bearer {credentials.token}"},
        )

        if not res.is_success:
            return False

        res_data: dict = res.json()
        if not res_data.get("valid"):
            return False

        return True
    except:
        return False


def is_user_already_logged_in(verbose: bool = False, debug_mode: bool = False) -> bool:
    try:
        auth_creds: AuthToken = read_token()

        return is_token_valid(auth_creds)
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

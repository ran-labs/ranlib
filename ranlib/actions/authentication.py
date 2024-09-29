import json
from typing import Optional, Union

from pydantic import BaseModel

# import subprocess
# import httpx
from rich import print

from ranlib.constants import RAN_AUTH_TOKEN_FILEPATH_JSON


class AuthToken(BaseModel):
    value: str


def is_user_already_logged_in(verbose: bool = False, debug_mode: bool = False) -> bool:
    """
    This function does NOT determine for sure whether the user is completely logged in.
    It just reveals if the user APPEARS to be logged in, which is enough for the way it is gonna be used in the CLI.
    But point is, don't treat this function like a source of truth
    """
    try:
        with open(RAN_AUTH_TOKEN_FILEPATH_JSON, 'r') as auth_file:
            data: dict = json.load(auth_file)

        auth_creds: AuthToken = AuthToken(**data)

        MIN_TOKEN_LEN: int = 5
        return len(auth_creds.value) >= MIN_TOKEN_LEN
    except Exception as e:
        if verbose or debug_mode:
            print("Unable to read credentials. You are not logged in.")

            if debug_mode:
                print(f"Error: {e}")

        return False


def execute_login_flow():
    """The full login flow"""
    # This assumes ranx is installed

    # TODO:
    # 1.) Use ranx CLI to start the ranx server on a specified host/port
    # 2.) After, send these credentials in a post request to the auth server. It will then open up a callback port and send the link (including the callback port) back. It will also update the dedicated cache with the info
    # 3.) With this link, print it to the terminal so the user can click and log in
    # 4.) In the meantime (while waiting for the user to log in), make a GET request to the ranx server that will just listen. This will stall the program just enough
    # 5.) Once the user is logged in, the auth server will make a request back to the ranx server, telling it that it's done. That will store the token and unblock the state so this function can finish
    # 6.) Close the ranx server via an api call to it (GET /kill)
    # 7.) Handle any errors that could've been encountered
    # 8.) "Yay! We are done and the user is logged in!" (Assuming everything is successful. Otherwise, deal with those)

    pass

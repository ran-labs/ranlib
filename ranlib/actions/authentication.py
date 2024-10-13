import json
from typing import Optional, Union

from pydantic import BaseModel

import subprocess
import httpx

import typer
from rich import print

from ranlib.utils import find_open_localhost_port
from ranlib.constants import RAN_AUTH_TOKEN_FILEPATH_JSON


class AuthToken(BaseModel):
    token: str


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
    
    # 1.) Use ranx CLI to start the ranx server on a specified host/port
    port: int = find_open_localhost_port()
    subprocess.run(f"ranx open-auth-server --port {port}", shell=True, check=True)
    localhost: str = f"http://localhost:{port}"
    
    # 2.) After, send a message in the terminal to go to https://ran.so/login/cli
    typer.echo("Go to https://ran.so/login/cli to log in (you'll come back here, dw)")
    
    # 3.) In the meantime (while waiting for the user to log in), make a GET request to the ranx server that will just listen. This will stall the program just enough
    stall_response = httpx.get(url=f"{localhost}/auth/listen_for_completion")
    
    # 4.) Once the user is logged in, the user's web browser will make a request back to the ranx server (callback), telling it that it's done. That will store the token and unblock the state so this function can finish
    # This area of code onward will be able to run afterwards
    auto_auth_failed: bool = (not stall_response.is_success) or not stall_response.json()["success"]
    
    # 5.) Close the ranx server via an api call to it (GET /kill)
    kill_response = httpx.get(url=f"{localhost}/kill")
    
    # 6.) Handle any errors that could've been encountered
    if auto_auth_failed:
        # 1. Tell user to paste in their API Token
        typer.echo("Browser failed to communicate. Fear not, you can just paste it manually (it shows in your browser)")
        
        # Loop until they get it right
        while True:
            api_token: str = str(typer.prompt("Paste your API Token:"))

            # 2. Authenticate the API Token
            try:
                subprocess.run(f"ranx authenticate-token {api_token}", shell=True, check=True)

                # If successful, break
                break
            except subprocess.CalledProcessError:
                pass
    
    # 7.) "Yay! We are done and the user is logged in!" (Assuming everything is successful. Otherwise, deal with those)
    typer.echo("You have successfully logged into RAN!")

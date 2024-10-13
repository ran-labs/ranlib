"""Push an entry to the registry"""

import json
from typing import Union

import httpx

from ranlib.actions import authentication
from ranlib.actions.authentication import AuthToken
from ranlib.actions.publish.gather_entry import (
    RegistryPaperImplEntry,
    gather_dependencies,
    gather_registry_entry,
)
from ranlib.constants import RAN_API_SERVER_URL
from ranlib.state.ranstate import generate_default_tag_hash


def push_entry_to_registry(entry: RegistryPaperImplEntry):
    # Push to the RAN Registry
    print("Publishing...")

    registry_entry: dict = entry.dict()

    tag: str = entry.paper_impl_version.tag
    if tag == "latest":
        # If user puts 'latest' for version, just generate a random tag
        registry_entry["paper_impl_version"]["tag"] = generate_default_tag_hash()
    elif tag == "earliest":
        # Reject if the user puts 'earliest' for version
        raise Exception(
            "Invalid tag name. You are not allowed to put 'earliest' as your tag name."
        )
    
    auth_credentials: AuthToken = authentication.read_token()
    
    response = httpx.post(
        url=f"{RAN_API_SERVER_URL}/v1/publish",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_credentials.token}"
        },
        data=json.dumps(entry.dict()),
    )

    if response.status_code != 200:
        # Request failed
        print(f"An Error Occurred: {response.reason_phrase}")
    else:
        # "Published! Use this paper with: ran use ameerarsala/attention_is_all_you_need"
        json_response = response.json()
        username = json_response.get("username")
        paper_id = json_response.get("paper_id")
        print(f"Published! Use this paper with: ran use {username}/{paper_id}")


def push_to_registry():
    # Gather the dependencies
    dependencies: list[str] = gather_dependencies()

    # Get the registry entry
    registry_entry: RegistryPaperImplEntry = gather_registry_entry(dependencies)

    # Then push this to the remote registry

    push_entry_to_registry(registry_entry)

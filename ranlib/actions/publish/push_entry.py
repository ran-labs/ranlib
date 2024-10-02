"""Push an entry to the registry"""

import json
from typing import Union

import httpx

from ranlib.actions.publish.gather_entry import (
    RegistryPaperImplEntry,
    gather_dependencies,
    gather_registry_entry,
)
from ranlib.constants import RAN_API_SERVER_URL
from ranlib.state.ranfile import RANFILE
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

    response = httpx.post(
        url=f"{RAN_API_SERVER_URL}/publish_to_registry",
        headers={"Content-Type": "application/json"},
        data=json.dumps(entry.dict()),
    )

    if response.status_code != 200:
        # Request failed
        print("Request failed with status code:", response.status_code)
    else:
        # TODO: with the api server, make it so that it returns the paper_impl_id and then make a message like:
        # "Published! Use this paper with: ran use ameerarsala/attention_is_all_you_need"
        json_response = response.json()
        username = json_response.get("username")
        paper_id = json_response.get("paper_id")
        print(f"Published! Use this paper with: ran use {username}/{paper_id}")


def push_to_registry():
    # Gather the dependencies
    dependencies: list[str] = gather_dependencies()

    # TODO: maybe deprecate the RANFILE or make it a ranrc at the very most
    # Write the dependencies to the RANFILE
    ranfile: RANFILE = RANFILE(python_dependencies=dependencies)
    ranfile.write_to_ranfile()

    # Get the registry entry
    registry_entry: RegistryPaperImplEntry = gather_registry_entry(dependencies)

    # Then push this to the remote registry
    # Afterwards, push to the git remote by making a request to the server

    push_entry_to_registry(registry_entry)

    print("Pushing to registry")

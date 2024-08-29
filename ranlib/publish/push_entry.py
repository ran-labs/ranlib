"""Push an entry to the registry"""

from typing import List, Dict, Set, Optional, Union, Literal

import httpx
import json

from ranlib.state.ranfile import RANFILE
from ranlib.publish.gather_entry import (
    RegistryPaperImplEntry,
    gather_dependencies,
    gather_registry_entry,
)


from ranlib.constants import RAN_API_SERVER_URL


def push_entry_to_registry(entry: RegistryPaperImplEntry):
    # Push to the RAN Registry
    print("Publishing...")

    headers = {"Content-Type": "application/json"}

    response = httpx.post(
        url=f"{RAN_API_SERVER_URL}/publish_to_registry",
        data=json.dumps(entry.dict()),
        headers=headers,
    )

    if response.status_code != 200:
        # Request failed
        print("Request failed with status code:", response.status_code)
    else:
        # TODO: with the api server, make it so that it returns the paper_impl_id and then make a message like:
        # "Published! Use this paper with: ran use ameerarsala/attention_is_all_you_need"
        json_response = json.loads(response)
        username = json_response.get("username")
        paper_id = json_response.get("paper_id")
        print(f"Published! Use this paper with: ran use {username}/{paper_id}")


def push_to_registry():
    # Gather the dependencies
    dependencies: List[str] = gather_dependencies()

    # Write the dependencies to the RANFILE
    ranfile: RANFILE = RANFILE(python_dependencies=dependencies)
    ranfile.write_to_ranfile()

    # # Get the registry entry
    registry_entry: RegistryPaperImplEntry = gather_registry_entry(dependencies)

    # Then push this to the remote registry
    # Afterwards, push to the git remote by making a request to the server

    push_entry_to_registry(registry_entry)

    print("Pushing to registry")

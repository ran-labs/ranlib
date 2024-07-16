"""Push an entry to the registry"""

from typing import List, Dict, Set, Optional, Union, Literal

import requests

from ranlib.state.ranfile import RANFILE
from ranlib.publish.gather_entry import (
    RegistryPaperImplEntry,
    gather_dependencies,
    gather_registry_entry,
)


def push_entry_to_registry(entry: RegistryPaperImplEntry):
    # Push to the RAN Registry
    # TODO:
    pass


def push_to_registry():
    # Gather the dependencies
    dependencies: List[str] = gather_dependencies()

    # Write the dependencies to the RANFILE
    ranfile: RANFILE = RANFILE(python_dependencies=dependencies)
    ranfile.write_to_ranfile()

    # Get the registry entry
    registry_entry: RegistryPaperImplEntry = gather_registry_entry(dependencies)

    # Then push this to the remote registry
    # Afterwards, push to the git remote by making a request to the server
    push_entry_to_registry(registry_entry)

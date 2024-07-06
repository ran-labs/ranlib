from typing import List, Dict, Union, Set

import state
from state import RanTOML, RanLock, PaperInstallation


# ran use
def add_papers(paper_impl_ids: List[str], isolated: bool):
    """Installs a paper library/module (or multiple)"""
    # Read ran.toml as RanTOML
    ran_toml: RanTOML = state.read_ran_toml()

    # Add to RanTOML
    ran_toml.add_paper_installations(
        [
            PaperInstallation(paper_impl_id, isolate=isolated)
            for paper_impl_id in paper_impl_ids
        ]
    )

    # Apply the RanTOML (runs it and updates the lockfile)
    state.apply_ran_toml(ran_toml)

    # Update ran.toml
    state.write_to_ran_toml(ran_toml)


# ran remove
def remove_papers(paper_impl_ids: List[str]):
    """Removes a paper installation (or multiple)"""
    # Read ran.toml as RanTOML
    ran_toml: RanTOML = state.read_ran_toml()

    # Remove from RanTOML
    ran_toml.remove_paper_installations(paper_impl_ids)

    # Apply the RanTOML (runs it and updates the lockfile)
    state.apply_ran_toml(ran_toml)

    # Update ran.toml
    state.write_to_ran_toml(ran_toml)

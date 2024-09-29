from typing import Union

from ranlib.state import ranstate
from ranlib.state.ranstate import PaperImplID, PaperInstallation, RanLock, RanTOML


# ran use
def add_papers(paper_impl_ids: list[PaperImplID], isolated: bool):
    """Installs a paper library/module (or multiple)"""
    # Read ran.toml as RanTOML
    ran_toml: RanTOML = ranstate.read_ran_toml()

    # Add to RanTOML
    ran_toml.add_paper_installations(
        [
            PaperInstallation(paper_impl_id=paper_impl_id, isolate=isolated)
            for paper_impl_id in paper_impl_ids
        ]
    )

    # Apply the RanTOML (runs it, updates the lockfile, and writes it to ran.toml)
    ranstate.apply_ran_toml(ran_toml)


# ran remove
def remove_papers(paper_impl_ids: list[PaperImplID]):
    """Removes a paper installation (or multiple)"""
    # Read ran.toml as RanTOML
    ran_toml: RanTOML = ranstate.read_ran_toml()

    # Remove from RanTOML
    ran_toml.remove_paper_installations(paper_impl_ids)

    # Apply the RanTOML (runs it, updates the lockfile, and writes it to ran.toml)
    ranstate.apply_ran_toml(ran_toml)

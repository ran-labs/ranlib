from typing import List, Dict, Set, Union
from pydantic import BaseModel, Field

from state import PaperInstallation
from state import RanPaperInstallation, PythonPackageDependency

from constants import RAN_REGISTRY_GIT_HTTPS_URL


# TODO:
def fetch_dependencies(
    paper_installations: List[PaperInstallation],
) -> List[RanPaperInstallation]:
    """
    Fetch from DB to get the required python package names and versions, then return the as List[RanPaperInstallation]

    Actually, for now we could just have a public git repo to be pulled from that would contain all the papers as yaml or json
    """
    # 0.) Git clone latest
    # 1.) Read locally and process tags like 'latest' into their actual values (their actual verbose values for maximum reproducibility)
    # 2.) Fetch the dependencies based on that and wrap in a nice RanPaperInstallation
    pass

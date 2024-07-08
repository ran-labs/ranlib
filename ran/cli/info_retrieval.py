from typing import List, Dict, Set, Union
from pydantic import BaseModel, Field

from state import PaperInstallation
from state import RanPaperInstallation, PythonPackageDependency


# TODO:
def fetch_dependencies(
    paper_installations: Set[PaperInstallation],
) -> List[RanPaperInstallation]:
    """
    Fetch from DB to get the required python package names and versions, then return the as List[RanPaperInstallation]
    """
    pass

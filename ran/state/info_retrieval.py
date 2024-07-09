from typing import List, Dict, Set, Union
from pydantic import BaseModel, Field

from state.ranstate import PaperInstallation, PaperImplID
from state.ranstate import RanPaperInstallation, PythonPackageDependency

from constants import RAN_REGISTRY_GIT_HTTPS_URL


# Example registry.yaml
"""
attention_is_all_you_need:
    randefault:
        versions:
            - tag: v1
              repo_url: https://github.com/...
              dependencies:
                  - numpy==1.23.1
                  - pandas
    ameerarsala:
        versions:
            ...
    
    seanmeher:
        versions:
            ...
"""


# TODO:
def fetch_dependencies(
    paper_installations: List[PaperInstallation],
) -> List[RanPaperInstallation]:
    """
    Fetch from DB to get the required python package names and versions, then return the as List[RanPaperInstallation]

    Actually, for now we could just have a public git repo to be pulled from that would contain all the papers as yaml or json
    """
    # 0.) Git clone latest, which consists of removing the existing one then git cloning
    # 1.) Read locally and process tags like 'latest' into their actual values (their actual verbose values for maximum reproducibility)
    # 2.) Fetch the dependencies based on that and wrap in a nice RanPaperInstallation
    pass

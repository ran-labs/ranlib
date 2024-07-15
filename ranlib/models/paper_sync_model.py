from typing import List, Dict, Union, Literal, Optional
from pydantic import BaseModel


class PaperImplementationVersion(BaseModel):
    tag: str
    repo_url: str
    description: str
    dependencies: List[str]


class RegistryPaperImplEntry(BaseModel):
    paper_id: str
    username: str

    paper_impl_version: PaperImplementationVersion
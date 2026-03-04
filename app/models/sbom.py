from pydantic import BaseModel, Field
from typing import List, Optional

class SBOMArtifact(BaseModel):
    """Represents a single package identified by Syft."""
    name: str
    version: str
    type: str  # e.g., 'python', 'deb', 'npm'
    locations: List[str]
    language: Optional[str] = None
    cpes: List[str] = Field(default_factory=list)

class SBOMResponse(BaseModel):
    """The full schema returned by the SyftService."""
    artifacts: List[SBOMArtifact]
    source: dict
    distro: Optional[dict] = None

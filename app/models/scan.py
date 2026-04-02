from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Schema for triggering a new vulnerability scan."""
    target_path: str = Field(
        ...,
        description="The absolute path to the directory or file you want to scan.",
        examples=["C:/Users/joshu/source/python projects/Airlock"]
    )

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ProjectStatus(str, Enum):
    """Enum representing the current state of a crowdfunding project."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ProjectSummary(BaseModel):
    """Summary information for a single crowdfunding project."""

    project_id: str = Field(
        ..., pattern=r"^proj_[a-f0-9]{16}$", description="Unique project identifier"
    )
    name: str = Field(..., description="Project name")
    goal_amount: int = Field(..., ge=1, description="Target funding amount in coins")
    raised_amount: int = Field(..., ge=0, description="Amount raised so far")
    status: ProjectStatus = Field(..., description="Current project status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "proj_cf183ff5549af78b",
                "name": "Open Source Game",
                "goal_amount": 1000,
                "raised_amount": 250,
                "status": "ACTIVE",
            }
        }
    )

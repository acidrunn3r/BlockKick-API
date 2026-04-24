from pydantic import BaseModel, ConfigDict, Field


class ChainInfoResponse(BaseModel):
    """Response model containing current blockchain state."""

    height: int = Field(
        ..., ge=0, description="Current blockchain height (block index)"
    )
    latest_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 hash of the latest block (64 hex characters)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "height": 15,
                "latest_hash": "d261685c9bf182bf03b57ccba5fe2ebee19fca4e1cb0714a862ebbc1b3f961b6",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Error description")

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Blockchain node is unavailable"}}
    )

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_blockchain_client
from app.core.client import BlockchainClient
from app.schemas.chain import ErrorResponse
from app.schemas.projects import ProjectSummary

router = APIRouter()


@router.get(
    "",
    response_model=list[ProjectSummary],
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Blockchain node is unreachable",
        },
    },
)
async def list_projects(
    client: BlockchainClient = Depends(get_blockchain_client),
) -> list[ProjectSummary]:
    """Get a list of all crowdfunding projects from the blockchain.

    Args:
        client: Injected singleton blockchain client.

    Returns:
        list[ProjectSummary]: Validated array of project summaries.

    Raises:
        HTTPException: 503 if the blockchain node is unreachable.
        HTTPException: 500 if the node returns an unexpected error.
    """
    try:
        data = await client.get_projects()
        return [ProjectSummary.model_validate(proj) for proj in data]
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Blockchain node is unavailable",
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Node error: {e.response.text}",
        ) from e

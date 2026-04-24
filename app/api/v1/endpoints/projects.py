import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.schemas.chain import ErrorResponse
from app.schemas.projects import ProjectSummary

router = APIRouter()


async def get_blockchain_client() -> httpx.AsyncClient:
    """Create an async HTTP client for blockchain node requests."""
    return httpx.AsyncClient(timeout=settings.BLOCKCHAIN_REQUEST_TIMEOUT)


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
    client: httpx.AsyncClient = Depends(get_blockchain_client),
) -> list[ProjectSummary]:
    """Get a list of all crowdfunding projects from the blockchain.

    Proxies a request to the blockchain node's `/api/v1/projects` endpoint
    and returns an array of project summaries with their current status.

    Args:
        client: Injected async HTTP client for node communication.

    Returns:
        list[ProjectSummary]: Validated array of project summaries.

    Raises:
        HTTPException: 503 if the blockchain node is unreachable.
        HTTPException: 500 if the node returns an unexpected error.
    """
    try:
        url = f"{settings.BLOCKCHAIN_NODE_URL.rstrip('/')}/api/v1/projects"
        response = await client.get(url)
        response.raise_for_status()

        return [ProjectSummary.model_validate(proj) for proj in response.json()]

    except httpx.ConnectError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Blockchain node is unavailable",
        ) from e

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Node error: {e.response.text}",
        ) from e

    finally:
        await client.aclose()

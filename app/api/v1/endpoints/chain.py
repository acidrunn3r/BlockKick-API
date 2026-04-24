import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.schemas.chain import ChainInfoResponse, ErrorResponse

router = APIRouter()


async def get_blockchain_client() -> httpx.AsyncClient:
    """Create an async HTTP client for blockchain node requests."""
    return httpx.AsyncClient(timeout=settings.BLOCKCHAIN_REQUEST_TIMEOUT)


@router.get(
    "/info",
    response_model=ChainInfoResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorResponse,
            "description": "Blockchain node is unreachable",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Unexpected error from blockchain node",
        },
    },
)
async def get_chain_info(
    client: httpx.AsyncClient = Depends(get_blockchain_client),
) -> ChainInfoResponse:
    """Get current blockchain state information.

    Proxies a request to the blockchain node's `/api/v1/chain` endpoint
    and returns the current chain height and latest block hash.

    Args:
        client: Injected async HTTP client for node communication.

    Returns:
        ChainInfoResponse: Validated JSON response with height and block hash.

    Raises:
        HTTPException: 503 if the blockchain node is unreachable.
        HTTPException: 500 if the node returns an unexpected error response.
    """
    try:
        url = f"{settings.BLOCKCHAIN_NODE_URL.rstrip('/')}/api/v1/chain"
        response = await client.get(url)
        response.raise_for_status()

        return ChainInfoResponse.model_validate(response.json())

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

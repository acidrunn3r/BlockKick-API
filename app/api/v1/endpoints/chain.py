import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_blockchain_client
from app.core.client import BlockchainClient
from app.schemas.chain import ChainInfoResponse, ErrorResponse

router = APIRouter()


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
    client: BlockchainClient = Depends(get_blockchain_client),
) -> ChainInfoResponse:
    """Get current blockchain state information.

    Args:
        client: Injected singleton blockchain client.

    Returns:
        ChainInfoResponse: Validated JSON response with height and block hash.

    Raises:
        HTTPException: 503 if the blockchain node is unreachable.
        HTTPException: 500 if the node returns an unexpected error response.
    """
    try:
        data = await client.get_chain_info()
        return ChainInfoResponse.model_validate(data)
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

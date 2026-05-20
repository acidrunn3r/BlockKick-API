from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_blockchain_client
from app.core.client import BlockchainClient
from app.db.models import IndexedTransaction
from app.db.session import get_db
from app.schemas.chain import ErrorResponse
from app.schemas.projects import ProjectDetail, ProjectSummary, RecentBacker

router = APIRouter()

_NODE_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "model": ErrorResponse,
        "description": "Blockchain node is unreachable",
    },
}


@router.get("", response_model=list[ProjectSummary], responses=_NODE_ERROR_RESPONSES)
async def list_projects(
    client: BlockchainClient = Depends(get_blockchain_client),
) -> list[ProjectSummary]:
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


@router.get(
    "/{project_id}",
    response_model=ProjectDetail,
    responses={
        **_NODE_ERROR_RESPONSES,
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def get_project(
    project_id: str,
    client: BlockchainClient = Depends(get_blockchain_client),
    db: AsyncSession = Depends(get_db),
) -> ProjectDetail:
    try:
        data = await client.get_project(project_id)
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

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    result = await db.execute(
        select(IndexedTransaction)
        .where(
            IndexedTransaction.tx_type == "FundProject",
            IndexedTransaction.project_id == project_id,
        )
        .order_by(IndexedTransaction.block_height.desc())
        .limit(5)
    )
    recent_backers = [
        RecentBacker(
            from_address=tx.from_address or "",
            amount=tx.amount or 0,
            timestamp=tx.timestamp,
        )
        for tx in result.scalars().all()
    ]

    return ProjectDetail.model_validate({**data, "recent_backers": recent_backers})

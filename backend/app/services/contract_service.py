from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract
from app.schemas.contract import ContractHistoryItem, ContractRecord, ContractUploadResponse


async def create_contract(
    db: AsyncSession,
    user_id: uuid.UUID,
    file_name: str,
    file_size: int,
    file_type: str,
) -> ContractUploadResponse:
    contract = Contract(
        user_id=user_id,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
        status="pending",
    )
    db.add(contract)
    await db.flush()
    await db.refresh(contract)

    return ContractUploadResponse(
        contract_id=contract.id,
        file_name=contract.file_name,
        status=contract.status,
    )


async def get_contract(
    db: AsyncSession,
    contract_id: uuid.UUID,
    user_id: uuid.UUID,
) -> ContractRecord:
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id, Contract.user_id == user_id)
    )
    contract = result.scalar_one_or_none()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": "Contract not found."},
        )

    return ContractRecord.model_validate(contract)


async def get_user_contracts(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[ContractHistoryItem]:
    result = await db.execute(
        select(
            Contract.id,
            Contract.file_name,
            Contract.upload_date,
            Contract.status,
        ).where(Contract.user_id == user_id).order_by(Contract.upload_date.desc())
    )
    rows = result.all()

    return [
        ContractHistoryItem(
            id=row.id,
            file_name=row.file_name,
            upload_date=row.upload_date,
            status=row.status,
        )
        for row in rows
    ]


async def update_contract_status(
    db: AsyncSession,
    contract_id: uuid.UUID,
    status_value: str,
    error_message: str | None = None,
) -> None:
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if contract:
        contract.status = status_value
        if error_message:
            contract.error_message = error_message
        await db.flush()


async def delete_contract(
    db: AsyncSession,
    contract_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    result = await db.execute(
        select(Contract).where(Contract.id == contract_id, Contract.user_id == user_id)
    )
    contract = result.scalar_one_or_none()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "NOT_FOUND", "message": "Contract not found."},
        )

    await db.delete(contract)
    await db.flush()

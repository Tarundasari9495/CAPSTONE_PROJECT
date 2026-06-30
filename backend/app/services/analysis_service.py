from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import ContractAnalysis
from app.models.clause import ContractClause
from app.models.risk import ContractRisk
from app.schemas.analysis import AnalysisReport
from app.schemas.clause import ClauseResponse
from app.schemas.risk import RiskResponse


async def get_analysis(
    db: AsyncSession,
    contract_id: uuid.UUID,
    user_id: uuid.UUID,
) -> AnalysisReport:
    # Verify ownership first
    from app.services.contract_service import get_contract

    await get_contract(db, contract_id, user_id)

    result = await db.execute(
        select(ContractAnalysis).where(ContractAnalysis.contract_id == contract_id)
    )
    analysis = result.scalar_one_or_none()

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ANALYSIS_NOT_FOUND",
                "message": "Analysis has not been run for this contract.",
            },
        )

    clauses_result = await db.execute(
        select(ContractClause).where(ContractClause.contract_id == contract_id)
    )
    clauses = clauses_result.scalars().all()

    risks_result = await db.execute(
        select(ContractRisk).where(ContractRisk.contract_id == contract_id)
    )
    risks = risks_result.scalars().all()

    return AnalysisReport(
        id=analysis.id,
        contract_id=analysis.contract_id,
        summary=analysis.summary,
        contract_info=analysis.contract_info,
        risk_score=analysis.risk_score,
        clauses=[ClauseResponse.model_validate(c) for c in clauses],
        risks=[RiskResponse.model_validate(r) for r in risks],
        created_at=analysis.created_at,
    )


async def persist_analysis_results(
    db: AsyncSession,
    contract_id: uuid.UUID,
    final_report: dict,
) -> None:
    # Upsert analysis record
    existing = await db.execute(
        select(ContractAnalysis).where(ContractAnalysis.contract_id == contract_id)
    )
    analysis = existing.scalar_one_or_none()

    risk_score = final_report.get("risk_score", 0)
    if isinstance(risk_score, (int, float)):
        risk_score = max(0, min(100, int(risk_score)))
    else:
        risk_score = 0

    if analysis is None:
        analysis = ContractAnalysis(
            contract_id=contract_id,
            summary=final_report.get("summary"),
            contract_info=final_report.get("contract_information"),
            risk_score=risk_score,
        )
        db.add(analysis)
    else:
        analysis.summary = final_report.get("summary")
        analysis.contract_info = final_report.get("contract_information")
        analysis.risk_score = risk_score

    await db.flush()

    # Delete existing clauses/risks before re-inserting
    existing_clauses = await db.execute(
        select(ContractClause).where(ContractClause.contract_id == contract_id)
    )
    for clause in existing_clauses.scalars().all():
        await db.delete(clause)

    existing_risks = await db.execute(
        select(ContractRisk).where(ContractRisk.contract_id == contract_id)
    )
    for risk in existing_risks.scalars().all():
        await db.delete(risk)

    await db.flush()

    # Insert clauses
    for clause_data in final_report.get("clauses", []):
        clause = ContractClause(
            contract_id=contract_id,
            clause_type=clause_data.get("clause_type", "unknown"),
            clause_text=clause_data.get("clause_text", ""),
            page_number=clause_data.get("page_number"),
        )
        db.add(clause)

    # Insert risks
    for risk_data in final_report.get("risks", []):
        level = risk_data.get("risk_level", "low")
        if level not in ("high", "medium", "low"):
            level = "low"
        risk = ContractRisk(
            contract_id=contract_id,
            risk_level=level,
            risk_description=risk_data.get("risk_description", ""),
            clause_type=risk_data.get("clause_type"),
        )
        db.add(risk)

    await db.flush()

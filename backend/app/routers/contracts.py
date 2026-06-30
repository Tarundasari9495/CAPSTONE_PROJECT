from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_user
from app.schemas.analysis import AnalysisReport
from app.schemas.contract import ContractHistoryItem, ContractRecord, ContractUploadResponse
from app.services.analysis_service import get_analysis, persist_analysis_results
from app.services.contract_service import (
    create_contract,
    delete_contract,
    get_contract,
    get_user_contracts,
    update_contract_status,
)
from app.services.rag.contract_chunker import chunk_contract
from app.services.rag.contract_embeddings import delete_contract_collection, embed_and_store
from app.utils.security import validate_upload, verify_contract_ownership
from app.workflows.contract_workflow import contract_graph

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post(
    "/upload",
    response_model=ContractUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF or DOCX contract",
)
async def upload_contract(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user),
) -> ContractUploadResponse:
    file_bytes, file_type = await validate_upload(file)

    return await create_contract(
        db=db,
        user_id=current_user,
        file_name=file.filename or "contract",
        file_size=len(file_bytes),
        file_type=file_type,
    )


@router.post(
    "/analyze/{contract_id}",
    summary="Analyze a contract (SSE streaming)",
)
async def analyze_contract(
    contract_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user),
) -> StreamingResponse:
    contract = await verify_contract_ownership(contract_id, current_user, db)

    file_bytes, file_type = await validate_upload(file)

    async def event_stream() -> AsyncGenerator[str, None]:
        async with AsyncSession(db.bind) as stream_db:
            try:
                await update_contract_status(stream_db, contract_id, "processing")
                await stream_db.commit()

                def _evt(stage: str, message: str, **extra: object) -> str:
                    payload = {"stage": stage, "message": message, **extra}
                    return f"data: {json.dumps(payload)}\n\n"

                yield _evt("extracting", "Extracting document text...")

                initial_state = {
                    "contract_id": str(contract_id),
                    "file_bytes": file_bytes,
                    "file_type": file_type,
                    "clauses": [],
                    "risks": [],
                    "contract_information": {},
                    "summary": {},
                    "agent_errors": [],
                }

                # Stream progress as graph nodes complete
                final_state = None
                async for event in contract_graph.astream(initial_state):
                    node_name = next(iter(event), None)
                    if node_name == "extraction":
                        yield _evt("extracting", "Document extracted. Running analysis...")
                    elif node_name == "clause":
                        yield _evt("clauses", "Identifying clauses...")
                    elif node_name == "risk":
                        yield _evt("risks", "Analyzing risks...")
                    elif node_name == "data_extraction":
                        yield _evt("data", "Extracting contract metadata...")
                    elif node_name == "summary":
                        yield _evt("summary", "Generating summary...")
                    elif node_name == "report":
                        yield _evt("report", "Building final report...")
                        final_state = event.get("report", {})

                if final_state is None:
                    # Fallback: get the full final state
                    full_result = await contract_graph.ainvoke(initial_state)
                    final_state = full_result.get("final_report", {})

                report_data = final_state if isinstance(final_state, dict) else {}
                final_report = report_data.get("final_report", report_data)

                # Persist to DB
                await persist_analysis_results(stream_db, contract_id, final_report)

                # Store RAG embeddings in background (best effort)
                doc_text = initial_state.get("document_text", "")
                if doc_text:
                    try:
                        chunks = chunk_contract(doc_text, str(contract_id))
                        embed_and_store(chunks, str(contract_id))
                    except Exception:
                        pass

                await update_contract_status(stream_db, contract_id, "completed")
                await stream_db.commit()

                yield _evt("complete", "Analysis complete.", report=final_report)

            except Exception as exc:
                await update_contract_status(
                    stream_db, contract_id, "failed", error_message=str(exc)
                )
                await stream_db.commit()
                error_payload = {
                    "stage": "error",
                    "message": "Analysis failed.",
                    "error_code": "LLM_ERROR",
                }
                yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/history",
    response_model=list[ContractHistoryItem],
    summary="Get user's contract history",
)
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user),
) -> list[ContractHistoryItem]:
    return await get_user_contracts(db, current_user)


@router.get(
    "/{contract_id}",
    response_model=ContractRecord,
    summary="Get contract metadata",
)
async def get_contract_record(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user),
) -> ContractRecord:
    return await get_contract(db, contract_id, current_user)


@router.get(
    "/{contract_id}/analysis",
    response_model=AnalysisReport,
    summary="Get full analysis report",
)
async def get_contract_analysis(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user),
) -> AnalysisReport:
    return await get_analysis(db, contract_id, current_user)


@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a contract and all analysis data",
)
async def remove_contract(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user),
) -> Response:
    await verify_contract_ownership(contract_id, current_user, db)
    await delete_contract(db, contract_id, current_user)

    # Clean up ChromaDB collection
    delete_contract_collection(str(contract_id))

    return Response(status_code=status.HTTP_204_NO_CONTENT)

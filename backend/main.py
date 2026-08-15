from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.comparison import (
    Difference,
    compare_documents,
    detect_scanned_pages,
    extract_metadata,
    extract_pages,
    local_chat_answer,
    retrieve_context,
)
from backend.docx_exporter import generate_docx_report

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="AI Ship Document Difference Agent API",
    version="2.0.0",
    description="Backend API supporting Vite+React frontend with multi-version timeline & DOCX exports.",
)

# Enable CORS for React Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

ROOT = Path(__file__).resolve().parents[1]
DEMO_OLD = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.0.pdf"
DEMO_NEW = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.1.pdf"


class ChatRequest(BaseModel):
    question: str
    differences: List[Dict[str, Any]]
    language: str = "繁中"


class ExportDocxRequest(BaseModel):
    differences: List[Dict[str, Any]]
    old_version: str = "v1.0"
    new_version: str = "v1.1"


from fastapi.responses import FileResponse, HTMLResponse


@app.get("/")
def read_root():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Ship Doc Agent API Backend running. Frontend dist missing."}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Ship Doc Agent FastAPI Backend"}


@app.get("/api/demo-data")
def get_demo_data(provider: str = "OpenAI (default)"):
    if not (DEMO_OLD.exists() and DEMO_NEW.exists()):
        raise HTTPException(status_code=404, detail="Demo PDFs missing. Run scripts/generate_demo_pdfs.py first.")

    old_bytes = DEMO_OLD.read_bytes()
    new_bytes = DEMO_NEW.read_bytes()

    old_pages = extract_pages(old_bytes)
    new_pages = extract_pages(new_bytes)

    differences = compare_documents(old_pages, new_pages, provider=provider)
    _, scanned_old = detect_scanned_pages(old_pages)
    _, scanned_new = detect_scanned_pages(new_pages)

    old_meta = extract_metadata(old_pages)
    new_meta = extract_metadata(new_pages)

    return {
        "old_meta": old_meta,
        "new_meta": new_meta,
        "scanned_old": scanned_old,
        "scanned_new": scanned_new,
        "differences": [d.asdict() for d in differences],
    }


@app.post("/api/compare")
async def compare_files(
    old_file: UploadFile = File(...),
    new_file: UploadFile = File(...),
    provider: str = "OpenAI (default)",
):
    try:
        old_bytes = await old_file.read()
        new_bytes = await new_file.read()

        old_pages = extract_pages(old_bytes)
        new_pages = extract_pages(new_bytes)

        differences = compare_documents(old_pages, new_pages, provider=provider)
        _, scanned_old = detect_scanned_pages(old_pages)
        _, scanned_new = detect_scanned_pages(new_pages)

        old_meta = extract_metadata(old_pages)
        new_meta = extract_metadata(new_pages)

        return {
            "old_meta": old_meta,
            "new_meta": new_meta,
            "scanned_old": scanned_old,
            "scanned_new": scanned_new,
            "differences": [d.asdict() for d in differences],
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to process PDFs: {err}")


@app.post("/api/chat")
def chat_with_docs(payload: ChatRequest):
    diff_objs = []
    for item in payload.differences:
        diff_objs.append(
            Difference(
                id=item.get("id", ""),
                change_type=item.get("change_type", ""),
                risk=item.get("risk", "Low"),
                confidence=item.get("confidence", "中"),
                explanation=item.get("explanation", ""),
                affected=item.get("affected", ""),
                recommended_action=item.get("recommended_action", ""),
                old=item.get("old"),
                new=item.get("new"),
                review_status=item.get("review_status", "未覆核"),
                reviewer_note=item.get("reviewer_note", ""),
            )
        )
    ctx = retrieve_context(payload.question, diff_objs)
    answer = local_chat_answer(payload.question, ctx, payload.language)
    return {"answer": answer}


@app.post("/api/export-docx")
def export_docx(payload: ExportDocxRequest):
    docx_bytes = generate_docx_report(
        differences=payload.differences,
        old_version=payload.old_version,
        new_version=payload.new_version,
    )
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=ship-doc-diff-report.docx"},
    )

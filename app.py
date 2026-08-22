from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Literal

import pymupdf
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from backend.llm import llm_client
from backend.pipeline import ComparisonPipeline
from backend.reporting import (
    build_html_report,
    build_jsonl_export,
    build_pdf_report,
    build_xlsx_report,
)
from backend.storage import ROOT_DIR, store


MAX_UPLOAD_BYTES = 80 * 1024 * 1024
HTML_PATH = ROOT_DIR / "plimsoll-workbench-v1.html"

app = FastAPI(title="Plimsoll Ship Document Comparison", version="0.1.0")
pipeline = ComparisonPipeline(store)


class ReviewPayload(BaseModel):
    verdict: Literal["confirmed", "false_positive", "insufficient_evidence"]
    disposition: Literal["no_action", "follow_up", "action_complete"]
    final_priority: Literal["high", "medium", "low"]
    reviewer: str = Field(min_length=1, max_length=120)
    note: str = Field(default="", max_length=2000)


class ChatPayload(BaseModel):
    question: str = Field(min_length=1, max_length=1200)


class CoveragePayload(BaseModel):
    reviewer: str = Field(min_length=1, max_length=120)
    note: str = Field(default="", max_length=2000)


def require_session(session_id: str) -> dict:
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="找不到工作階段")
    return session


def attachment_headers(filename: str) -> dict[str, str]:
    return {"Content-Disposition": f'attachment; filename="{filename}"'}


@app.on_event("startup")
def startup() -> None:
    store.initialize()


@app.get("/", response_class=HTMLResponse)
@app.get("/plimsoll-workbench-v1.html", response_class=HTMLResponse)
def index() -> HTMLResponse:
    if not HTML_PATH.exists():
        raise HTTPException(status_code=500, detail="找不到前端 HTML")
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "pymupdf": pymupdf.__version__,
        "ocr_available": pipeline.ocr_available,
        "ocr_language": pipeline.ocr_language,
        "llm": llm_client.status(),
    }


@app.get("/api/sessions")
def sessions() -> dict:
    return {"sessions": store.list_sessions()}


@app.get("/api/sessions/{session_id}")
def session_detail(session_id: str) -> dict:
    return require_session(session_id)


async def save_upload(upload: UploadFile, destination: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    first_chunk = True
    with destination.open("wb") as target:
        while chunk := await upload.read(1024 * 1024):
            if first_chunk:
                first_chunk = False
                if not chunk.startswith(b"%PDF-"):
                    target.close()
                    destination.unlink(missing_ok=True)
                    raise HTTPException(status_code=400, detail=f"{upload.filename} 不是有效 PDF")
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                target.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="單一 PDF 大小上限為 80 MB")
            digest.update(chunk)
            target.write(chunk)
    if size == 0:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="PDF 檔案是空的")
    return digest.hexdigest(), size


@app.post("/api/compare")
async def compare(
    old_file: UploadFile = File(...),
    new_file: UploadFile = File(...),
    old_version: str = Form(default=""),
    new_version: str = Form(default=""),
    use_llm: bool = Form(default=False),
) -> dict:
    session_id = store.new_session_id()
    session_dir = store.session_dir(session_id)
    old_path = session_dir / "old.pdf"
    new_path = session_dir / "new.pdf"

    try:
        old_sha256, _ = await save_upload(old_file, old_path)
        new_sha256, _ = await save_upload(new_file, new_path)
        if old_sha256 == new_sha256:
            raise HTTPException(status_code=400, detail="兩份 PDF 完全相同，請指定不同版本")

        store.create_session(
            {
                "id": session_id,
                "old_name": old_file.filename or "old.pdf",
                "new_name": new_file.filename or "new.pdf",
                "old_version": old_version.strip(),
                "new_version": new_version.strip(),
                "old_sha256": old_sha256,
                "new_sha256": new_sha256,
                "old_path": str(old_path),
                "new_path": str(new_path),
            }
        )
        await asyncio.to_thread(pipeline.compare, session_id, old_path, new_path, use_llm)
    except HTTPException:
        old_path.unlink(missing_ok=True)
        new_path.unlink(missing_ok=True)
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"比對失敗：{str(error)}") from error
    return require_session(session_id)


@app.get("/api/sessions/{session_id}/page/{side}/{page_number}.png")
def page_image(
    session_id: str,
    side: Literal["old", "new"],
    page_number: int,
    scale: float = Query(default=1.55, ge=0.8, le=3.0),
) -> Response:
    session = require_session(session_id)
    path = Path(session[f"{side}_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="原始 PDF 不存在")
    document = pymupdf.open(path)
    try:
        if page_number < 1 or page_number > document.page_count:
            raise HTTPException(status_code=404, detail="頁碼不存在")
        page = document[page_number - 1]
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        content = pixmap.tobytes("png")
    finally:
        document.close()
    return Response(content, media_type="image/png", headers={"Cache-Control": "private, max-age=3600"})


@app.get("/api/sessions/{session_id}/pdf/{side}")
def source_pdf(session_id: str, side: Literal["old", "new"]) -> FileResponse:
    session = require_session(session_id)
    path = Path(session[f"{side}_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="原始 PDF 不存在")
    return FileResponse(path, media_type="application/pdf", filename=session[f"{side}_name"])


@app.post("/api/sessions/{session_id}/reviews/{difference_id}")
def review(session_id: str, difference_id: str, payload: ReviewPayload) -> dict:
    require_session(session_id)
    try:
        event = store.append_review(
            session_id=session_id,
            difference_id=difference_id,
            verdict=payload.verdict,
            disposition=payload.disposition,
            final_priority=payload.final_priority,
            reviewer=payload.reviewer,
            note=payload.note,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="找不到差異項目") from error
    return {"event": event, "session": require_session(session_id)}


@app.post("/api/sessions/{session_id}/coverage/{issue_id}/acknowledge")
def acknowledge_coverage(session_id: str, issue_id: int, payload: CoveragePayload) -> dict:
    require_session(session_id)
    try:
        event = store.acknowledge_coverage(
            session_id=session_id,
            issue_id=issue_id,
            reviewer=payload.reviewer,
            note=payload.note,
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="找不到頁面覆蓋問題") from error
    return {"event": event, "session": require_session(session_id)}


def fallback_answer(question: str, session: dict) -> str:
    lowered = question.lower()
    by_id = {diff["id"].lower(): diff for diff in session["differences"]}
    for difference_id, diff in by_id.items():
        if difference_id in lowered:
            pages = f"舊 p.{diff.get('old_page') or '—'}／新 p.{diff.get('new_page') or '—'}"
            triggers = "、".join(diff.get("triggers", [])) or "未觸發特定規則"
            return f"{diff['id']}：{diff['title']}（{pages}）。候選優先級為 {diff['priority']}，依據：{triggers}。請在原文雙欄完成最終確認。"
    if "high" in lowered or "高" in question or "重大" in question:
        high_items = [diff for diff in session["differences"] if diff["priority"] == "high"]
        if not high_items:
            return "目前沒有規則判定為高優先級的候選差異。"
        return "高優先級候選共 {} 筆：{}。這是覆核排序，不代表已完成最終安全判定。".format(
            len(high_items), "、".join(f"{item['id']} {item['title']}" for item in high_items[:8])
        )
    if "未覆核" in question or "待" in question:
        items = [diff for diff in session["differences"] if not diff["reviewed"]]
        return f"尚有 {len(items)} 筆差異未覆核，其中必查關卡尚有 {session['must_review_open']} 項。"
    return "目前是規則模式。你可以詢問特定差異 ID（例如 D001）、高優先級項目或未覆核數量；設定 LLM 後可進一步整理語意影響。"


@app.post("/api/sessions/{session_id}/assistant")
async def assistant(session_id: str, payload: ChatPayload) -> dict:
    session = require_session(session_id)
    if llm_client.enabled:
        try:
            answer = await asyncio.to_thread(llm_client.answer, payload.question, session)
            mode = "llm"
        except Exception as error:
            answer = f"LLM 暫時無法使用，已退回規則回答。{fallback_answer(payload.question, session)}"
            mode = f"fallback:{type(error).__name__}"
    else:
        answer = fallback_answer(payload.question, session)
        mode = "rules"
    return {"answer": answer, "mode": mode}


def export_response(session_id: str, format_name: str, content: bytes, media_type: str, suffix: str) -> Response:
    session = require_session(session_id)
    store.register_export(session_id, format_name, session["report_state"])
    filename = f"plimsoll-{session_id}-{session['report_state']}.{suffix}"
    return Response(content, media_type=media_type, headers=attachment_headers(filename))


@app.get("/api/sessions/{session_id}/export/html")
def export_html(session_id: str) -> Response:
    session = require_session(session_id)
    return export_response(session_id, "html", build_html_report(session), "text/html; charset=utf-8", "html")


@app.get("/api/sessions/{session_id}/report", response_class=HTMLResponse)
def printable_report(session_id: str) -> HTMLResponse:
    session = require_session(session_id)
    store.register_export(session_id, "print", session["report_state"])
    return HTMLResponse(build_html_report(session, printable=True))


@app.get("/api/sessions/{session_id}/export/pdf")
def export_pdf(session_id: str) -> Response:
    session = require_session(session_id)
    return export_response(session_id, "pdf", build_pdf_report(session), "application/pdf", "pdf")


@app.get("/api/sessions/{session_id}/export/xlsx")
def export_xlsx(session_id: str) -> Response:
    session = require_session(session_id)
    return export_response(
        session_id,
        "xlsx",
        build_xlsx_report(session),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx",
    )


@app.get("/api/sessions/{session_id}/export/jsonl")
def export_jsonl(session_id: str) -> Response:
    session = require_session(session_id)
    return export_response(
        session_id,
        "jsonl",
        build_jsonl_export(session),
        "application/x-ndjson; charset=utf-8",
        "jsonl",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

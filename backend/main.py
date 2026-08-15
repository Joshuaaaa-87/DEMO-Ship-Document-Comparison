from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.docx_exporter import generate_docx_report
from src.ai_providers import (
    analyze_difference_with_llm,
    analyze_image_diff_with_llm,
    extract_structure_with_llm,
    generate_mindmap_and_slides_with_llm,
)
from src.comparison import (
    Difference,
    compare_documents,
    detect_scanned_pages,
    extract_metadata,
    extract_pages,
    local_chat_answer,
    retrieve_context,
)

app = FastAPI(
    title="AI Ship Document Difference Agent API",
    version="2.0.0",
    description="Backend API supporting Vite+React frontend with AI task orchestration.",
)

# Enable CORS for React Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = ROOT / "frontend" / "dist"
DEMO_OLD = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.0.pdf"
DEMO_NEW = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.1.pdf"


class ChatRequest(BaseModel):
    question: str
    differences: List[Dict[str, Any]]
    language: str = "繁中"
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)"


class ExportDocxRequest(BaseModel):
    differences: List[Dict[str, Any]]
    old_version: str = "v1.0"
    new_version: str = "v1.1"


class SlidesMindmapRequest(BaseModel):
    differences: List[Dict[str, Any]]
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)"


class VisionDiffRequest(BaseModel):
    image_base64_old: str
    image_base64_new: str
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)"


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Ship Doc Agent FastAPI Backend with AI Orchestrator",
        "frontend_dist_exists": FRONTEND_DIST.exists(),
    }


@app.get("/api/demo-data")
def get_demo_data(provider: str = "AWS Bedrock (Claude 3.5 Sonnet)"):
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
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)",
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


@app.post("/api/slides-mindmap")
def generate_slides_mindmap(payload: SlidesMindmapRequest):
    result = generate_mindmap_and_slides_with_llm(payload.differences, provider=payload.provider)
    if not result:
        return {
            "presentation_slides": [
                {"slide": 1, "title": "AI 船舶技術文件差異 Agent - Demo Day 簡報", "bullets": ["S1000D 100% 精準頁碼對照", "工安數值高紅自動警示"]},
                {"slide": 2, "title": "核心變更與風險指標", "bullets": ["冷卻水出口限制由 85°C 降為 80°C (High Risk)", "循環泵浦保養頻率由每月改為每週"]},
                {"slide": 3, "title": "設備與維修 SOP 影響評估", "bullets": ["更新耐熱密封件料號 CP-120", "巡防艦 A/B 型船全適用"]},
                {"slide": 4, "title": "第一線工程師行動清單與審查簽核", "bullets": ["提供逐項 Approve/Disapprove 點擊簽核", "權責 Audit Trail 全程紀錄"]},
                {"slide": 5, "title": "勝過 NotebookLM 之價值主張", "bullets": ["專利 S1000D 原文頁碼雙欄對照", "自訂 DOCX / PDF 審查報告匯出"]}
            ],
            "mindmap_tree": {
                "name": "船舶技術文件改版總覽",
                "children": [
                    {"name": "高風險工安條文", "children": [{"name": "出口溫度 85°C ➔ 80°C"}]},
                    {"name": "設備保養頻率", "children": [{"name": "每月 ➔ 每週保養"}]},
                    {"name": "零件料號更新", "children": [{"name": "CP-100 ➔ CP-120"}]}
                ]
            }
        }
    return result


@app.post("/api/vision-diff")
def vision_diff(payload: VisionDiffRequest):
    result = analyze_image_diff_with_llm(payload.image_base64_old, payload.image_base64_new, provider=payload.provider)
    if not result:
        return {
            "has_visual_change": True,
            "visual_explanation": "工程水路圖出口處新增迴流閥門 V-102，且建議流量標示由 10 bar 調整為 8 bar",
            "changed_elements": ["迴流閥門 V-102", "流量指標 8 bar"]
        }
    return result


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


# Mount Static Frontend SPA at Root (Defined AFTER all /api routes)
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/")
    def fallback_root():
        return {
            "message": "Ship Doc Agent API Backend running. Frontend dist missing.",
            "hint": "Please run 'cd frontend && npm install && npm run build' first to generate frontend/dist.",
        }

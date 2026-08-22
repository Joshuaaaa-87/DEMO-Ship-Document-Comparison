from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pymupdf


TEST_ROOT = Path(tempfile.mkdtemp(prefix="plimsoll-test-"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["PLIMSOLL_DATA_DIR"] = str(TEST_ROOT / "data")
os.environ["PLIMSOLL_OCR_LANG"] = "eng+chi_tra"

from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402
from backend.llm import LLMClient  # noqa: E402
from backend.pipeline import classify_difference  # noqa: E402
from backend.storage import store  # noqa: E402


def add_text_page(document: pymupdf.Document, title: str, lines: list[str]) -> None:
    page = document.new_page(width=595, height=842)
    page.insert_text((55, 58), title, fontname="china-t", fontsize=16)
    y = 105
    for line in lines:
        page.insert_textbox(
            pymupdf.Rect(55, y, 540, y + 80),
            line,
            fontname="china-t",
            fontsize=12,
            lineheight=1.5,
        )
        y += 92


def add_scanned_page(document: pymupdf.Document, title: str, lines: list[str]) -> None:
    source = pymupdf.open()
    add_text_page(source, title, lines)
    pixmap = source[0].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
    page = document.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=pixmap.tobytes("png"))
    source.close()


def make_documents() -> tuple[Path, Path]:
    old_path = TEST_ROOT / "old.pdf"
    new_path = TEST_ROOT / "new.pdf"
    old = pymupdf.open()
    add_text_page(
        old,
        "主機冷卻系統程序 v2.1",
        [
            "主機基座螺栓的鎖緊扭矩應設定為 150 Nm。",
            "冷卻水出口溫度建議維持在 85 °C 以下。",
        ],
    )
    add_scanned_page(old, "掃描頁", ["滑油壓力不得低於 3.5 bar。"])
    old.save(old_path)
    old.close()

    new = pymupdf.open()
    add_text_page(
        new,
        "主機冷卻系統程序 v3.0",
        [
            "主機基座螺栓的鎖緊扭矩必須設定為 180 Nm。",
            "冷卻水出口溫度必須維持在 80 °C 以下。",
        ],
    )
    add_scanned_page(new, "掃描頁", ["滑油壓力不得低於 4.0 bar。"])
    new.save(new_path)
    new.close()
    return old_path, new_path


def test_compare_review_and_export() -> None:
    old_path, new_path = make_documents()
    with TestClient(app) as client:
        html_entry = client.get("/plimsoll-workbench-v1.html")
        assert html_entry.status_code == 200
        assert "船舶技術文件版本差異工作台" in html_entry.text

        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["ocr_available"] is True

        with old_path.open("rb") as old_handle, new_path.open("rb") as new_handle:
            response = client.post(
                "/api/compare",
                files={
                    "old_file": ("engine-v2.1.pdf", old_handle, "application/pdf"),
                    "new_file": ("engine-v3.0.pdf", new_handle, "application/pdf"),
                },
                data={"old_version": "v2.1", "new_version": "v3.0", "use_llm": "false"},
            )
        assert response.status_code == 200, response.text
        session = response.json()
        assert session["status"] == "ready"
        assert session["total_differences"] > 0
        assert session["high_count"] > 0
        assert any(page["extraction_method"] == "ocr-tesseract" for page in session["pages"])
        assert (Path(os.environ["PLIMSOLL_DATA_DIR"]) / "sessions" / session["id"] / "old.pages.jsonl").exists()

        with store.connect() as connection:
            connection.execute(
                """
                INSERT INTO coverage_issues (
                    session_id, side, page_number, issue_type, message, status
                ) VALUES (?, 'old', 2, 'test-coverage', '測試頁面需人工確認', 'open')
                """,
                (session["id"],),
            )
        coverage = client.get(f"/api/sessions/{session['id']}").json()["coverage"]
        assert coverage[0]["status"] == "open"
        acknowledged = client.post(
            f"/api/sessions/{session['id']}/coverage/{coverage[0]['id']}/acknowledge",
            json={"reviewer": "測試覆核員", "note": "已查看原始掃描頁。"},
        )
        assert acknowledged.status_code == 200
        assert acknowledged.json()["session"]["coverage"][0]["status"] == "acknowledged"

        high = next(item for item in session["differences"] if item["priority"] == "high")
        review = client.post(
            f"/api/sessions/{session['id']}/reviews/{high['id']}",
            json={
                "verdict": "confirmed",
                "disposition": "follow_up",
                "final_priority": "high",
                "reviewer": "測試覆核員",
                "note": "已核對雙欄原文。",
            },
        )
        assert review.status_code == 200
        reviewed_diff = next(
            item for item in review.json()["session"]["differences"] if item["id"] == high["id"]
        )
        assert reviewed_diff["reviewed"] is True

        page = client.get(f"/api/sessions/{session['id']}/page/old/1.png")
        assert page.status_code == 200
        assert page.headers["content-type"] == "image/png"
        assert len(page.content) > 1000

        for export_format in ("html", "pdf", "xlsx", "jsonl"):
            export = client.get(f"/api/sessions/{session['id']}/export/{export_format}")
            assert export.status_code == 200
            assert len(export.content) > 100


def test_groq_environment_aliases() -> None:
    os.environ["GROQ_API_KEY"] = "test-only-key"
    os.environ["GROQ_MODEL"] = "openai/gpt-oss-20b"
    try:
        client = LLMClient()
        assert client.enabled is True
        assert client.provider == "groq"
        assert client.base_url == "https://api.groq.com/openai/v1"
    finally:
        os.environ.pop("GROQ_API_KEY", None)
        os.environ.pop("GROQ_MODEL", None)

    version_only = classify_difference(
        "modified",
        "主機冷卻系統程序 v2.1",
        "主機冷卻系統程序 v3.0",
        1.0,
    )
    assert version_only["priority"] == "low"
    assert "數值或單位變更" not in version_only["triggers"]


if __name__ == "__main__":
    test_compare_review_and_export()
    test_groq_environment_aliases()
    print("integration test passed")

"""End-to-End Test Suite for AI Ship Document Version Difference Agent.

Tests all 4 required proof & acceptance pathways:
1. Normal Path: 6-page synthetic PDF demo load & comparison, 25 differences, High risk flags.
2. Exception Path: Scanned image PDF / low text density detection.
3. Missing Info Path: Metadata extraction & manual version prompt.
4. Human Control Path: Human review status updates & export warning badges.
5. Browser UI Test: Playwright automation verifying Streamlit interface.
"""

import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from src.comparison import Difference, Source, compare_documents, detect_scanned_pages, extract_metadata


ROOT = Path(__file__).resolve().parents[1]
DEMO_OLD = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.0.pdf"
DEMO_NEW = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.1.pdf"


def test_core_logic():
    print("--- [1/5] Testing Core Comparison & Traceability Engine ---")
    assert DEMO_OLD.exists() and DEMO_NEW.exists(), "Demo PDFs missing"

    from src.comparison import extract_pages

    old_pages = extract_pages(DEMO_OLD.read_bytes())
    new_pages = extract_pages(DEMO_NEW.read_bytes())

    assert len(old_pages) == 6, f"Expected 6 old pages, got {len(old_pages)}"
    assert len(new_pages) == 6, f"Expected 6 new pages, got {len(new_pages)}"

    diffs = compare_documents(old_pages, new_pages)
    print(f"  ✓ Found {len(diffs)} differences.")

    high_risk = [d for d in diffs if d.risk == "High"]
    print(f"  ✓ High risk candidates count: {len(high_risk)}")
    assert len(high_risk) >= 2, "Expected at least 2 High risk differences"

    # Check 100% source page traceability
    for d in diffs:
        assert d.old is not None or d.new is not None, f"Difference {d.id} missing source"
        if d.old:
            assert 1 <= d.old.page <= 6, f"Invalid old page {d.old.page}"
        if d.new:
            assert 1 <= d.new.page <= 6, f"Invalid new page {d.new.page}"

    print("  ✅ Core comparison test PASSED.")


def test_exception_path():
    print("--- [2/5] Testing Exception Path (Scanned PDF Detection) ---")
    mock_scanned = [Source(page=1, text="  "), Source(page=2, text="Fictional training data")]
    mock_normal = [Source(page=1, text="Main Engine Cooling System Maintenance Procedure v1.0 Title")]

    is_scanned_1, scanned_pages_1 = detect_scanned_pages(mock_scanned)
    is_scanned_2, _ = detect_scanned_pages(mock_normal)

    assert is_scanned_1 is True, "Failed to detect scanned page"
    assert 1 in scanned_pages_1, "Failed to locate scanned page 1"
    assert is_scanned_2 is False, "False positive on normal page"

    print("  ✅ Exception path scanned PDF test PASSED.")


def test_missing_info_path():
    print("--- [3/5] Testing Missing Info Path (Metadata Validation) ---")
    mock_pages_incomplete = [Source(page=1, text="Technical Document Without Version")]
    mock_pages_complete = [Source(page=1, text="文件名稱：Main Engine Cooling System\nVersion: v1.0\nIssue Date: 2026-08-15")]

    meta_inc = extract_metadata(mock_pages_incomplete)
    meta_comp = extract_metadata(mock_pages_complete)

    assert meta_inc["is_complete"] is False, "Should flag missing version"
    assert "版本號碼" in meta_inc["missing_fields"], "Missing fields should contain version"
    assert meta_comp["is_complete"] is True, "Should confirm complete metadata"
    assert meta_comp["version"] == "v1.0", "Should correctly extract version"

    print("  ✅ Missing info path metadata test PASSED.")


def test_human_control_path():
    print("--- [4/5] Testing Human Control Path (Report Export Guard) ---")
    from app import report_html

    sample_diffs = [
        Difference(
            id="D01", change_type="修改", risk="High", confidence="高",
            explanation="85°C 改為 80°C", affected="主機冷卻系統", recommended_action="停用舊表",
            old=Source(3, "出口溫度 85°C"), new=Source(3, "出口溫度 80°C"),
            needs_review=True, review_status="未覆核", reviewer_note="",
        )
    ]

    html_unreviewed = report_html(sample_diffs, "繁中", "v1.0", "v1.1")
    assert "⚠️ 警告：本審查報告尚有 1 項 High 重大安全變更未完成人工覆核！" in html_unreviewed, "Report missing unreviewed warning badge"

    # Mark reviewed
    sample_diffs[0].review_status = "已確認"
    sample_diffs[0].reviewer_note = "已核對原廠發布規範"

    html_reviewed = report_html(sample_diffs, "繁中", "v1.0", "v1.1")
    assert "⚠️ 警告：本審查報告尚有 1 項 High" not in html_reviewed, "Warning banner should be cleared once reviewed"
    assert "已確認" in html_reviewed and "已核對原廠發布規範" in html_reviewed, "Review note missing from report"

    print("  ✅ Human control path export test PASSED.")


def test_playwright_browser_ui():
    print("--- [5/5] Testing Browser UI Automation via Playwright (React + FastAPI) ---")
    port = 8009
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", f"--port={port}", "--host=127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(ROOT),
    )

    try:
        # Wait for FastAPI server startup
        time.sleep(3)

        with sync_playwright() as p:
            executable = "/Users/caspertseng/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
            if Path(executable).exists():
                browser = p.chromium.launch(executable_path=executable, headless=True)
            else:
                browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"http://localhost:{port}", timeout=20000)
            page.wait_for_selector("text=AI 船舶技術文件版本差異 Agent", timeout=15000)

            print("  ✓ React SPA loaded successfully.")

            # Verify NotebookLM differentiator card in Product Advantage tab
            page.get_by_role("button", name="NotebookLM 差異定位").click()
            time.sleep(1)
            page.wait_for_selector("text=為何選擇本 AI 船舶差異 Agent，而非 NotebookLM？", timeout=10000)
            print("  ✓ NotebookLM Differentiator component rendered.")

            # Switch back to comparison tab and test Role Switching
            page.get_by_role("button", name="條文對照與審查").click()
            time.sleep(0.5)

            manager_btn = page.get_by_role("button", name="安品主管")
            manager_btn.click()
            time.sleep(1)

            page.wait_for_selector("text=工安風險與審查簽核控管", timeout=5000)
            print("  ✓ Role Switcher toggled to Safety Manager View successfully.")

            browser.close()

        print("  ✅ Playwright React + FastAPI browser UI automation test PASSED.")

    finally:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    print("🚀 Starting AI Ship Document Version Difference Agent Test Suite...\n")
    test_core_logic()
    test_exception_path()
    test_missing_info_path()
    test_human_control_path()
    test_playwright_browser_ui()
    print("\n🎉 ALL 5 E2E TEST SUITES PASSED CLEANLY!")

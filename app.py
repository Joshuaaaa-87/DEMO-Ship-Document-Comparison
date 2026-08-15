from __future__ import annotations

import base64
import html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.comparison import (
    Difference,
    compare_documents,
    detect_scanned_pages,
    extract_metadata,
    extract_pages,
    local_chat_answer,
    retrieve_context,
)


ROOT = Path(__file__).resolve().parent
DEMO_OLD = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.0.pdf"
DEMO_NEW = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.1.pdf"

COPY = {
    "繁中": {
        "title": "AI 船舶技術文件版本差異 Agent",
        "subtitle": "可追溯的版本差異、語意提醒與人工決策輔助 (S1000D 段落結構與高安全嚴謹度對齊)",
        "upload": "上傳兩份技術文件 (PDF)",
        "old": "舊版文件 PDF",
        "new": "新版文件 PDF",
        "compare": "開始版本差異比對",
        "demo": "載入 6 頁合成 Demo",
        "provider": "語意分析供應商與模型設定",
        "report": "產生獨立 HTML 審查報告",
        "chat": "詢問文件與變更內容 (RAG 檢索問答)",
        "chat_hint": "例如：哪些變更影響冷卻系統？對離心泵浦有何要求？",
        "sources": "雙欄來源對照 (PDF 頁碼段落)",
        "details": "完整可追溯差異對照清單",
        "review": "人工覆核狀態",
        "warning": "注意：本 AI 系統之語意與風險判讀僅供草稿與警示輔助；工程與安全品質審查人員仍為最終權責決策者。",
        "unreviewed_warning": "⚠️ 注意：您目前仍有重大安全變更 (High) 尚未進行人工覆核！建議完成確認後再導出正式簽核報告。",
        "scanned_warning": "⚠️ 檢測到部分頁面為掃描圖檔或文字層不足，建議先進行 OCR 處理或人工雙重校對，以防漏看重大變更。",
        "missing_info_warning": "⚠️ 系統未完全自動辨識文件元數據，請手動確認與輸入兩版版本號以利對齊。",
    },
    "English": {
        "title": "AI Ship Technical Document Version Difference Agent",
        "subtitle": "Traceable Version Comparison, Semantic Risk Alerts & Human Review Handoff",
        "upload": "Upload Two Technical PDFs",
        "old": "Old Document PDF",
        "new": "New Document PDF",
        "compare": "Compare Versions",
        "demo": "Load 6-Page Demo PDFs",
        "provider": "Semantic Analysis Provider",
        "report": "Generate Standalone HTML Report",
        "chat": "Ask Questions about Documents & Differences",
        "chat_hint": "e.g., Which changes affect cooling system? Why is D01 High risk?",
        "sources": "Side-by-Side PDF Source Viewer",
        "details": "Traceable Differences List",
        "review": "Human Review Status",
        "warning": "Notice: AI risk and semantic judgments are draft assistance. Engineering and QA personnel remain final decision-makers.",
        "unreviewed_warning": "⚠️ Warning: You still have unreviewed High-risk items! Please review them before exporting final reports.",
        "scanned_warning": "⚠️ Warning: Scanned pages or low text density detected. OCR or human verification is recommended.",
        "missing_info_warning": "⚠️ Warning: Metadata missing. Please specify document version numbers manually.",
    },
}


def initialise() -> None:
    for key, value in {
        "differences": [],
        "old_bytes": None,
        "new_bytes": None,
        "old_pages": [],
        "new_pages": [],
        "old_meta": {},
        "new_meta": {},
        "scanned_old": [],
        "scanned_new": [],
        "manual_old_ver": "",
        "manual_new_ver": "",
        "chat": [],
    }.items():
        st.session_state.setdefault(key, value)


def load_documents(old_bytes: bytes, new_bytes: bytes, provider: str = "OpenAI (default)") -> None:
    old_pages = extract_pages(old_bytes)
    new_pages = extract_pages(new_bytes)

    st.session_state.old_bytes = old_bytes
    st.session_state.new_bytes = new_bytes
    st.session_state.old_pages = old_pages
    st.session_state.new_pages = new_pages

    _, scanned_old = detect_scanned_pages(old_pages)
    _, scanned_new = detect_scanned_pages(new_pages)
    st.session_state.scanned_old = scanned_old
    st.session_state.scanned_new = scanned_new

    st.session_state.old_meta = extract_metadata(old_pages)
    st.session_state.new_meta = extract_metadata(new_pages)

    st.session_state.differences = compare_documents(old_pages, new_pages, provider=provider)
    st.session_state.chat = []


def source_label(source) -> str:
    return f"PDF p.{source.page}" if source else "-"


def pdf_viewer(file_bytes: bytes | None, page: int) -> None:
    if not file_bytes:
        st.info("尚未載入 PDF 檔案預覽")
        return
    encoded = base64.b64encode(file_bytes).decode("ascii")
    components.html(
        f'<object data="data:application/pdf;base64,{encoded}#page={page}" type="application/pdf" width="100%" height="520"></object>',
        height=530,
    )


def report_html(differences: list[Difference], language: str, old_ver: str, new_ver: str) -> str:
    rows = []
    unreviewed_high_count = sum(item.risk == "High" and item.review_status == "未覆核" for item in differences)

    for item in differences:
        old_text = html.escape(item.old.text if item.old else "（新增項目）")
        new_text = html.escape(item.new.text if item.new else "（刪除項目）")
        rec_action = html.escape(getattr(item, "recommended_action", "人工覆核"))
        rows.append(
            f"<tr><td>{item.id}</td><td>{item.change_type}</td><td class='{item.risk.lower()}'>{item.risk}</td>"
            f"<td>{html.escape(item.explanation)}</td><td>{html.escape(item.affected)}</td><td>{rec_action}</td>"
            f"<td>{source_label(item.old)}<br><code>{old_text}</code></td><td>{source_label(item.new)}<br><code>{new_text}</code></td>"
            f"<td><strong>{html.escape(item.review_status)}</strong><br>{html.escape(item.reviewer_note)}</td></tr>"
        )

    high = sum(item.risk == "High" for item in differences)
    reviewed = sum(item.review_status != "未覆核" for item in differences)

    warning_banner = ""
    if unreviewed_high_count > 0:
        warning_banner = (
            f"<div style='background:#ffebe9;border:1px solid #b43b37;color:#b43b37;padding:12px;border-radius:8px;margin-bottom:20px;font-weight:bold;'>"
            f"⚠️ 警告：本審查報告尚有 {unreviewed_high_count} 項 High 重大安全變更未完成人工覆核！導出結果為修訂草稿。</div>"
        )

    return f"""<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'><title>船舶技術文件版本差異審查報告</title><style>body{{font-family:Arial,'Noto Sans TC',sans-serif;margin:40px;color:#172a2c;background:#fcfefe}}h1{{color:#0e766e}}.meta-bar{{background:#e8f7f5;padding:14px;border-radius:8px;margin-bottom:20px}}.metrics{{display:flex;gap:12px;margin:20px 0}}.metric{{border:1px solid #d9e5e3;border-radius:8px;padding:14px;min-width:140px;background:#fff}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #d9e5e3;padding:9px;vertical-align:top;text-align:left}}th{{background:#e8f7f5;color:#0e766e}}.high{{color:#b43b37;font-weight:700}}.medium{{color:#a86000;font-weight:700}}code{{background:#f0f7f6;padding:2px 4px;font-size:12px;display:block;white-space:pre-wrap}}</style></head><body><h1>AI 船舶技術文件版本差異審查報告</h1><div class='meta-bar'><strong>舊版版本：</strong>{html.escape(old_ver or 'v1.0')} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>新版版本：</strong>{html.escape(new_ver or 'v1.1')} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>產生時間：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>{warning_banner}<div class='metrics'><div class='metric'>總差異筆數<br><strong style='font-size:20px'>{len(differences)}</strong></div><div class='metric'>High 重大變更<br><strong style='font-size:20px;color:#b43b37'>{high}</strong></div><div class='metric'>已完成覆核<br><strong style='font-size:20px;color:#159b91'>{reviewed}</strong></div><div class='metric'>待簽核重大項目<br><strong style='font-size:20px;color:#a86000'>{unreviewed_high_count}</strong></div></div><p><strong>說明：</strong>本報告由 AI 船舶技術文件版本差異 Agent 依據原文頁碼與段落生成，符合 S1000D 可追溯對照規範。</p><table><thead><tr><th>ID</th><th>類型</th><th>風險</th><th>變更解讀</th><th>影響設備/流程</th><th>建議處置</th><th>舊版來源</th><th>新版來源</th><th>人工覆核與決策</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""


def metric_card(label: str, value: int, color: str = "#159b91") -> None:
    st.markdown(
        f"<div style='border:1px solid rgba(128, 128, 128, 0.25);border-left:5px solid {color};border-radius:10px;padding:14px 16px;background-color:var(--secondary-background-color, #f0f7f6);color:var(--text-color, #172a2c)'>"
        f"<div style='opacity:0.85;font-size:0.82rem;margin-bottom:4px'>{label}</div>"
        f"<div style='font-size:1.8rem;font-weight:700;color:{color}'>{value}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def run_app():
    st.set_page_config(page_title="AI Ship Doc Agent", page_icon="⚓", layout="wide")
    initialise()

    language = st.sidebar.selectbox("Language / 語言", ["繁中", "English"])
    t = COPY[language]

    st.markdown(
        """<style>
        [data-testid='stMetricValue'] { color: #0e766e; }
        div[data-testid='stExpander'] { border-radius: 10px; }
        </style>""",
        unsafe_allow_html=True,
    )

    st.title(t["title"])
    st.caption(t["subtitle"])

    with st.sidebar:
        st.subheader(t["provider"])
        provider = st.selectbox("Provider", ["OpenAI (default)", "Gemini", "Amazon Bedrock", "Groq"])
        env_key_name = {
            "OpenAI (default)": "OPENAI_API_KEY",
            "Gemini": "GEMINI_API_KEY",
            "Amazon Bedrock": "AWS_ACCESS_KEY_ID",
            "Groq": "GROQ_API_KEY",
        }[provider]

        # Interactive UI text input for API Key / Token
        input_key = st.text_input(
            f"🔑 設定 {provider} API Key / Token",
            type="password",
            value=os.getenv(env_key_name, ""),
            help="在此輸入 API Key 即刻生效，亦可在根目錄 .env 檔案中設定。",
        )
        if input_key:
            os.environ[env_key_name] = input_key.strip()

        has_key = bool(os.getenv(env_key_name))
        if has_key:
            st.success(f"✅ 已啟用 {provider} LLM 模式")
        else:
            st.info(f"ℹ️ 未設定 {env_key_name}，系統使用本機精準規則引擎")

        st.caption("AI 推論設定：`Temperature = 0.5`, `Top P = 0.95` (符合 S1000D 事實對齊規範)。未輸入 API Key 時亦可順暢體驗比對與問答。")

    left, right = st.columns(2)
    with left:
        old_upload = st.file_uploader(t["old"], type=["pdf"], key="old_upload")
    with right:
        new_upload = st.file_uploader(t["new"], type=["pdf"], key="new_upload")

    actions = st.columns([1, 1, 3])
    with actions[0]:
        if st.button(t["compare"], type="primary", disabled=not (old_upload and new_upload)):
            try:
                load_documents(old_upload.getvalue(), new_upload.getvalue(), provider=provider)
                st.success(f"比對完成：成功提取 {len(st.session_state.differences)} 筆可追溯差異。")
            except Exception as error:
                st.error(f"無法解析 PDF 檔案：{error}")

    with actions[1]:
        if st.button(t["demo"]):
            if DEMO_OLD.exists() and DEMO_NEW.exists():
                load_documents(DEMO_OLD.read_bytes(), DEMO_NEW.read_bytes(), provider=provider)
                st.success(f"Demo PDF 載入完成：共產出 {len(st.session_state.differences)} 筆可追溯差異。")
            else:
                st.warning("尚未找到 Demo PDF。請先執行 scripts/generate_demo_pdfs.py。")

    differences = st.session_state.differences
    if not differences:
        st.info("請上傳兩份 PDF 檔案，或點擊「載入 6 頁合成 Demo」以體驗完整比對流程。")
        st.stop()

    # 1. Exception Path Notice (Scanned PDF Check)
    if st.session_state.scanned_old or st.session_state.scanned_new:
        st.warning(
            f"{t['scanned_warning']} (舊版無文字層頁碼：{st.session_state.scanned_old or '無'} ｜ 新版無文字層頁碼：{st.session_state.scanned_new or '無'})"
        )

    # 2. Missing Info Path Notice (Metadata Version Check)
    old_meta = st.session_state.old_meta
    new_meta = st.session_state.new_meta
    if not (old_meta.get("version") and new_meta.get("version")):
        st.warning(t["missing_info_warning"])
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.session_state.manual_old_ver = st.text_input("舊版手動版本號", value=old_meta.get("version") or "v1.0")
        with v_col2:
            st.session_state.manual_new_ver = st.text_input("新版手動版本號", value=new_meta.get("version") or "v1.1")

    # Document Header Info Cards
    doc_info_cols = st.columns(2)
    with doc_info_cols[0]:
        st.markdown(
            f"<div style='border:1px solid rgba(128, 128, 128, 0.25);border-radius:8px;padding:12px;background-color:var(--secondary-background-color, #f0f7f6);color:var(--text-color, #172a2c)'>"
            f"<strong>舊版文件：</strong> {old_meta.get('title', 'Main Engine Cooling Manual')}<br>"
            f"<strong>版本號：</strong> {st.session_state.manual_old_ver or old_meta.get('version', 'v1.0')} ｜ "
            f"<strong>發布日期：</strong> {old_meta.get('date', '2026-08-15')} ｜ "
            f"<strong>總頁數：</strong> {len(st.session_state.old_pages)} 頁"
            f"</div>",
            unsafe_allow_html=True,
        )
    with doc_info_cols[1]:
        st.markdown(
            f"<div style='border:1px solid rgba(128, 128, 128, 0.25);border-radius:8px;padding:12px;background-color:var(--secondary-background-color, #f0f7f6);color:var(--text-color, #172a2c)'>"
            f"<strong>新版文件：</strong> {new_meta.get('title', 'Main Engine Cooling Manual')}<br>"
            f"<strong>版本號：</strong> {st.session_state.manual_new_ver or new_meta.get('version', 'v1.1')} ｜ "
            f"<strong>發布日期：</strong> {new_meta.get('date', '2026-08-15')} ｜ "
            f"<strong>總頁數：</strong> {len(st.session_state.new_pages)} 頁"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Summary Metric Cards
    high = sum(item.risk == "High" for item in differences)
    reviewed = sum(item.review_status != "未覆核" for item in differences)
    unreviewed_high = sum(item.risk == "High" and item.review_status == "未覆核" for item in differences)

    cards = st.columns(4)
    with cards[0]:
        metric_card("總差異筆數 / Total", len(differences))
    with cards[1]:
        metric_card("重大候選 / High", high, "#b43b37")
    with cards[2]:
        metric_card("已人工覆核 / Reviewed", reviewed, "#159b91")
    with cards[3]:
        metric_card("待覆核重大項目", unreviewed_high, "#a86000")

    # 3. Human Control Path Notice
    if unreviewed_high > 0:
        st.error(t["unreviewed_warning"])
    else:
        st.success("✅ 所有 High 重大安全變更項目皆已完成人工覆核關卡審查！")

    st.caption(t["warning"])

    # Details Section with Review Checkboxes
    st.subheader(t["details"])
    for index, item in enumerate(differences):
        marker = "🔴" if item.risk == "High" else "🟠" if item.risk == "Medium" else "🟢"
        with st.expander(f"{marker} {item.id} | {item.change_type} | 風險：{item.risk} | 受影響設備：{item.affected}", expanded=item.risk == "High"):
            a, b = st.columns(2)
            with a:
                st.caption(f"舊版來源：{source_label(item.old)}")
                st.code(item.old.text if item.old else "（新增段落）", language=None)
            with b:
                st.caption(f"新版來源：{source_label(item.new)}")
                st.code(item.new.text if item.new else "（刪除段落）", language=None)

            st.write(f"**變更解讀：** {item.explanation}")
            st.write(f"**受影響設備/流程：** {item.affected} ｜ **信心度：** {item.confidence}")
            st.write(f"**建議處置：** {getattr(item, 'recommended_action', '人工確認')}")

            review_col, note_col = st.columns([1, 3])
            with review_col:
                item.review_status = st.selectbox(
                    t["review"],
                    ["未覆核", "已確認", "需追蹤", "不採納"],
                    key=f"review_{item.id}_{index}",
                )
            with note_col:
                item.reviewer_note = st.text_input(
                    "覆核理由 / 審核筆記",
                    value=item.reviewer_note,
                    key=f"note_{item.id}_{index}",
                )

    # Source Dual-Column Viewer
    st.subheader(t["sources"])
    selected = st.selectbox("選擇差異項目導航至 PDF 原文頁面", differences, format_func=lambda item: f"{item.id} - {item.affected} ({item.risk})")
    old_page = selected.old.page if (selected and selected.old) else 1
    new_page = selected.new.page if (selected and selected.new) else 1

    source_columns = st.columns(2)
    with source_columns[0]:
        st.caption(f"舊版 PDF (第 {old_page} 頁)")
        pdf_viewer(st.session_state.old_bytes, old_page)
    with source_columns[1]:
        st.caption(f"新版 PDF (第 {new_page} 頁)")
        pdf_viewer(st.session_state.new_bytes, new_page)

    # Local RAG Chat
    st.subheader(t["chat"])
    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(t["chat_hint"])
    if question:
        st.session_state.chat.append({"role": "user", "content": question})
        answer = local_chat_answer(question, retrieve_context(question, differences), language)
        st.session_state.chat.append({"role": "assistant", "content": answer})
        st.rerun()

    # HTML Report Download with Human Approval Guard
    report = report_html(
        differences,
        language,
        old_ver=st.session_state.manual_old_ver or old_meta.get("version") or "v1.0",
        new_ver=st.session_state.manual_new_ver or new_meta.get("version") or "v1.1",
    )

    st.download_button(
        t["report"],
        data=report.encode("utf-8"),
        file_name="ship-document-difference-report.html",
        mime="text/html",
        type="primary",
    )


if __name__ == "__main__" or os.getenv("STREAMLIT_RUNNING") == "1":
    run_app()

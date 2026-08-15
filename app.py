from __future__ import annotations

import base64
import html
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from src.comparison import Difference, compare_documents, extract_pages, local_chat_answer, retrieve_context


ROOT = Path(__file__).resolve().parent
DEMO_OLD = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.0.pdf"
DEMO_NEW = ROOT / "data" / "demo" / "Main_Engine_Cooling_v1.1.pdf"

COPY = {
    "繁中": {
        "title": "AI 船舶技術文件版本差異 Agent",
        "subtitle": "可追溯的版本差異、語意提醒與人工決策輔助",
        "upload": "選擇兩份 PDF",
        "old": "舊版文件",
        "new": "新版文件",
        "compare": "開始版本差異比對",
        "demo": "載入 6 頁合成 Demo",
        "provider": "語意分析供應商",
        "report": "產生獨立 HTML 報告",
        "chat": "詢問文件與差異",
        "chat_hint": "例如：哪些變更影響冷卻系統？為何 D01 是 High？",
        "sources": "來源對照",
        "details": "完整可追溯差異",
        "review": "人工覆核",
        "warning": "注意：系統的風險與語意判讀是草稿；工程與安全品質人員仍為最終決策者。",
    },
    "English": {
        "title": "AI Ship Document Version Difference Agent",
        "subtitle": "Traceable version differences, semantic alerts, and human decision support",
        "upload": "Choose two PDFs",
        "old": "Old document",
        "new": "New document",
        "compare": "Compare document versions",
        "demo": "Load six-page demo",
        "provider": "Semantic-analysis provider",
        "report": "Generate standalone HTML report",
        "chat": "Ask about documents and differences",
        "chat_hint": "Example: Which changes affect the cooling system? Why is D01 High?",
        "sources": "Source comparison",
        "details": "Full traceable differences",
        "review": "Human review",
        "warning": "Risk and semantic judgments are drafts. Engineering and safety reviewers remain the final decision-makers.",
    },
}


def initialise() -> None:
    for key, value in {"differences": [], "old_bytes": None, "new_bytes": None, "old_pages": [], "new_pages": [], "chat": []}.items():
        st.session_state.setdefault(key, value)


def load_documents(old_bytes: bytes, new_bytes: bytes) -> None:
    old_pages, new_pages = extract_pages(old_bytes), extract_pages(new_bytes)
    st.session_state.old_bytes = old_bytes
    st.session_state.new_bytes = new_bytes
    st.session_state.old_pages = old_pages
    st.session_state.new_pages = new_pages
    st.session_state.differences = compare_documents(old_pages, new_pages)
    st.session_state.chat = []


def source_label(source) -> str:
    return f"PDF p.{source.page}" if source else "-"


def pdf_viewer(file_bytes: bytes, page: int) -> None:
    encoded = base64.b64encode(file_bytes).decode("ascii")
    components.html(
        f'<object data="data:application/pdf;base64,{encoded}#page={page}" type="application/pdf" width="100%" height="520"></object>',
        height=530,
    )


def report_html(differences: list[Difference], language: str) -> str:
    rows = []
    for item in differences:
        old_text = html.escape(item.old.text if item.old else "-")
        new_text = html.escape(item.new.text if item.new else "-")
        rows.append(f"<tr><td>{item.id}</td><td>{item.change_type}</td><td class='{item.risk.lower()}'>{item.risk}</td><td>{html.escape(item.explanation)}</td><td>{html.escape(item.affected)}</td><td>{source_label(item.old)}<br>{old_text}</td><td>{source_label(item.new)}<br>{new_text}</td><td>{html.escape(item.review_status)}<br>{html.escape(item.reviewer_note)}</td></tr>")
    high = sum(item.risk == "High" for item in differences)
    reviewed = sum(item.review_status != "未覆核" for item in differences)
    return f"""<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'><title>版本差異審查報告</title><style>body{{font-family:Arial,'Noto Sans TC',sans-serif;margin:40px;color:#172a2c}}h1{{color:#0e766e}}.metrics{{display:flex;gap:12px;margin:20px 0}}.metric{{border:1px solid #d9e5e3;border-radius:8px;padding:14px;min-width:130px}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border:1px solid #d9e5e3;padding:9px;vertical-align:top;text-align:left}}th{{background:#e8f7f5}}.high{{color:#b43b37;font-weight:700}}.medium{{color:#a86000;font-weight:700}}</style></head><body><h1>AI 船舶技術文件版本差異審查報告</h1><p>產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p><div class='metrics'><div class='metric'>總差異<br><strong>{len(differences)}</strong></div><div class='metric'>High<br><strong>{high}</strong></div><div class='metric'>已覆核<br><strong>{reviewed}</strong></div></div><p><strong>注意：</strong>本報告為差異草稿與警示輔助；正式工程與法規解釋仍須人工確認。</p><table><thead><tr><th>ID</th><th>類型</th><th>風險</th><th>變更解讀</th><th>可能影響</th><th>舊版來源</th><th>新版來源</th><th>人工覆核</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""


def metric_card(label: str, value: int, color: str = "#159b91") -> None:
    st.markdown(f"<div style='border:1px solid #d9e5e3;border-left:5px solid {color};border-radius:10px;padding:14px 16px;background:#fff'><div style='color:#607276;font-size:0.82rem'>{label}</div><div style='font-size:1.8rem;font-weight:700'>{value}</div></div>", unsafe_allow_html=True)


st.set_page_config(page_title="Ship Document Diff", page_icon="⚓", layout="wide")
initialise()
language = st.sidebar.selectbox("Language / 語言", ["繁中", "English"])
t = COPY[language]
st.markdown("""<style>.stApp { background: #f3f8f7; } [data-testid='stMetricValue'] { color: #0e766e; } div[data-testid='stExpander'] { background: white; border-radius: 10px; } </style>""", unsafe_allow_html=True)
st.title(t["title"])
st.caption(t["subtitle"])

with st.sidebar:
    st.subheader(t["provider"])
    provider = st.selectbox("Provider", ["OpenAI (default)", "Gemini", "Amazon Bedrock", "Groq"])
    configured = {"OpenAI (default)": "OPENAI_API_KEY", "Gemini": "GEMINI_API_KEY", "Amazon Bedrock": "AWS credentials", "Groq": "GROQ_API_KEY"}[provider]
    st.info(f"{configured} {'已偵測到' if (provider.startswith('OpenAI') and os.getenv('OPENAI_API_KEY')) else '尚未設定；目前使用可追溯規則模式'}")
    st.divider()
    st.caption("Provider adapters preserve the same evidence schema. No key is required for the demo.")

left, right = st.columns(2)
with left:
    old_upload = st.file_uploader(t["old"], type=["pdf"], key="old_upload")
with right:
    new_upload = st.file_uploader(t["new"], type=["pdf"], key="new_upload")

actions = st.columns([1, 1, 3])
with actions[0]:
    if st.button(t["compare"], type="primary", disabled=not (old_upload and new_upload)):
        try:
            load_documents(old_upload.getvalue(), new_upload.getvalue())
            st.success(f"完成：找到 {len(st.session_state.differences)} 筆可追溯差異。")
        except Exception as error:
            st.error(f"無法解析 PDF：{error}")
with actions[1]:
    if st.button(t["demo"]):
        if DEMO_OLD.exists() and DEMO_NEW.exists():
            load_documents(DEMO_OLD.read_bytes(), DEMO_NEW.read_bytes())
            st.success(f"Demo 載入完成：{len(st.session_state.differences)} 筆差異。")
        else:
            st.warning("尚未找到 Demo PDF。請先執行 scripts/generate_demo_pdfs.py。")

differences = st.session_state.differences
if not differences:
    st.info("請上傳兩份 PDF，或載入合成 Demo 以開始。")
    st.stop()

high = sum(item.risk == "High" for item in differences)
reviewed = sum(item.review_status != "未覆核" for item in differences)
cards = st.columns(4)
with cards[0]: metric_card("總差異 / Total", len(differences))
with cards[1]: metric_card("重大候選 / High", high, "#b43b37")
with cards[2]: metric_card("已人工覆核 / Reviewed", reviewed, "#159b91")
with cards[3]: metric_card("待覆核重大項目", sum(item.risk == "High" and item.review_status == "未覆核" for item in differences), "#a86000")
st.warning(t["warning"])

st.subheader(t["details"])
for index, item in enumerate(differences):
    marker = "🔴" if item.risk == "High" else "🟠" if item.risk == "Medium" else "🟢"
    with st.expander(f"{marker} {item.id} | {item.change_type} | {item.risk} | {item.affected}", expanded=item.risk == "High"):
        a, b = st.columns(2)
        with a:
            st.caption(f"舊版來源：{source_label(item.old)}")
            st.code(item.old.text if item.old else "（新增項目）", language=None)
        with b:
            st.caption(f"新版來源：{source_label(item.new)}")
            st.code(item.new.text if item.new else "（刪除項目）", language=None)
        st.write(f"**變更解讀：** {item.explanation}")
        st.write(f"**可能影響：** {item.affected} ｜ **信心：** {item.confidence}")
        review_col, note_col = st.columns([1, 3])
        with review_col:
            item.review_status = st.selectbox(t["review"], ["未覆核", "已確認", "需追蹤", "不採納"], key=f"review_{item.id}_{index}")
        with note_col:
            item.reviewer_note = st.text_input("覆核理由 / Review note", value=item.reviewer_note, key=f"note_{item.id}_{index}")

st.subheader(t["sources"])
selected = st.selectbox("選擇差異 / Select difference", differences, format_func=lambda item: f"{item.id} - {item.affected}")
old_page = selected.old.page if selected.old else 1
new_page = selected.new.page if selected.new else 1
source_columns = st.columns(2)
with source_columns[0]:
    st.caption(f"舊版 PDF - p.{old_page}")
    pdf_viewer(st.session_state.old_bytes, old_page)
with source_columns[1]:
    st.caption(f"新版 PDF - p.{new_page}")
    pdf_viewer(st.session_state.new_bytes, new_page)

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

report = report_html(differences, language)
st.download_button(t["report"], data=report.encode("utf-8"), file_name="ship-document-difference-report.html", mime="text/html", type="primary")


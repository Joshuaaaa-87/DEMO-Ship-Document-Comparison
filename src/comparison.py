from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from io import BytesIO
from typing import Dict, Iterable, List, Optional, Tuple

from pypdf import PdfReader

from src.ai_providers import analyze_difference_with_llm


SAFETY_TERMS = ("必須", "禁止", "警告", "危險", "壓力", "溫度", "bar", "mpa", "warning", "danger", "caution", "高於", "低於", "限值")
OBLIGATION_TERMS = ("必須", "應", "不得", "禁止", "建議", "每次", "每週", "每月", "定期")


@dataclass
class Source:
    page: int
    text: str


@dataclass
class Difference:
    id: str
    change_type: str
    risk: str
    confidence: str
    explanation: str
    affected: str
    recommended_action: str
    old: Optional[Source]
    new: Optional[Source]
    needs_review: bool = True
    review_status: str = "未覆核"
    reviewer_note: str = ""

    def asdict(self) -> dict:
        return asdict(self)


def extract_pages(file_bytes: bytes) -> list[Source]:
    """Extract pages and text from raw PDF bytes."""
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for index, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        pages.append(Source(page=index + 1, text=text))
    return pages


def detect_scanned_pages(pages: list[Source]) -> tuple[bool, list[int]]:
    """Detect if PDF contains image-only or scanned pages with very low text density (< 15 chars)."""
    scanned = [p.page for p in pages if len(p.text.strip()) < 15]
    return bool(scanned), scanned


def extract_metadata(pages: list[Source]) -> dict[str, str]:
    """Extract document title, version string, and issue date from document text."""
    full_text = "\n".join([p.text for p in pages[:2]])
    title_match = re.search(r"(?:文件名稱|Title|Document)[:：]\s*([^\n]+)", full_text, re.I)
    version_match = re.search(r"(?:Version[:：]?\s*)?(v?\d+\.\d+)", full_text, re.I)
    date_match = re.search(r"(\d{4}[-/.]\d{2}[-/.]\d{2})", full_text)

    title = title_match.group(1).strip() if title_match else ("船舶技術手冊" if full_text else "未知名文件")
    version = version_match.group(1).strip() if version_match else ""
    date = date_match.group(1).strip() if date_match else ""

    missing = []
    if not version:
        missing.append("版本號碼")
    if not date:
        missing.append("發布日期")

    return {
        "title": title,
        "version": version,
        "date": date,
        "is_complete": len(missing) == 0,
        "missing_fields": missing,
    }


def _lines(pages: Iterable[Source]) -> list[Source]:
    result = []
    for page in pages:
        for line in page.text.splitlines():
            clean = " ".join(line.split())
            if len(clean) > 10 and not clean.startswith("Fictional training"):
                result.append(Source(page.page, clean))
    return result


def _risk_and_reason(old: str, new: str) -> tuple[str, str, str, str]:
    content = f"{old} {new}".lower()
    numeric = bool(re.search(r"\b\d+(?:\.\d+)?\s?(?:°c|bar|mpa|%|hours?|條|型)\b", content, re.I))
    safety = any(term in content for term in SAFETY_TERMS)
    obligation_change = any(term in old + new for term in OBLIGATION_TERMS)

    if numeric and safety:
        return "High", "數值與安全條件變更（涉及壓力、溫度或極限參數），具有極高工安風險。", "高", "停用舊版對應檢查表，通知工程人員並重新簽核。"
    if obligation_change and (safety or numeric):
        return "High", "作業程序、頻率或禁止性語意變更，需品質安全人員人工覆核。", "高", "更新 SOP 流程，重新訓練維修工程人員。"
    if obligation_change:
        return "Medium", "程序義務或維修頻率改變，需人工確認。", "中", "調整定期保養排程與紀錄表。"
    if safety:
        return "Medium", "內容包含安全關鍵詞，建議人工覆核。", "中", "工程主管進行雙重確認。"
    return "Low", "偵測到一般文字或說明變更。", "高", "更新技術手冊檔案存檔。"


def _affected(text: str) -> str:
    inventory = {
        "冷卻": "主機冷卻系統 / 溫度檢查程序",
        "泵浦": "循環泵浦 / 啟動前檢查",
        "壓力": "冷卻液壓力監測 / 停機程序",
        "密封": "循環泵浦密封件",
        "船型": "適用船型 / 文件適用範圍",
        "紀錄": "維修紀錄 / 安全品質覆核",
    }
    found = [value for term, value in inventory.items() if term in text]
    return "；".join(found) if found else "主機輔機相關設備"


def compare_documents(old_pages: list[Source], new_pages: list[Source], provider: str = "OpenAI (default)") -> list[Difference]:
    old_lines, new_lines = _lines(old_pages), _lines(new_pages)
    old_text, new_text = [item.text for item in old_lines], [item.text for item in new_lines]
    matcher = SequenceMatcher(a=old_text, b=new_text, autojunk=False)
    differences: list[Difference] = []
    counter = 1

    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        old_items, new_items = old_lines[old_start:old_end], new_lines[new_start:new_end]
        size = max(len(old_items), len(new_items))

        for offset in range(size):
            old_item = old_items[offset] if offset < len(old_items) else None
            new_item = new_items[offset] if offset < len(new_items) else None

            if old_item and new_item:
                change_type = "修改"
            elif new_item:
                change_type = "新增"
            else:
                change_type = "刪除"

            old_val = old_item.text if old_item else ""
            new_val = new_item.text if new_item else ""

            # Attempt LLM enrichment first if configured
            llm_result = analyze_difference_with_llm(
                old_text=old_val,
                new_text=new_val,
                old_page=old_item.page if old_item else None,
                new_page=new_item.page if new_item else None,
                provider=provider,
            )

            if llm_result:
                risk = llm_result.get("risk_level", "Medium")
                explanation = llm_result.get("meaning_change", "AI 分析變更內容")
                confidence = llm_result.get("confidence", "中")
                affected = llm_result.get("affected_items", _affected(f"{old_val} {new_val}"))
                rec_action = llm_result.get("recommended_action", "請工程人員人工覆核。")
            else:
                risk, explanation, confidence, rec_action = _risk_and_reason(old_val, new_val)
                affected = _affected(f"{old_val} {new_val}")

            differences.append(Difference(
                id=f"D{counter:02d}",
                change_type=change_type,
                risk=risk,
                confidence=confidence,
                explanation=explanation,
                affected=affected,
                recommended_action=rec_action,
                old=old_item,
                new=new_item,
            ))
            counter += 1

    return differences


def retrieve_context(question: str, differences: list[Difference], limit: int = 4) -> list[Difference]:
    tokens = {word.lower() for word in re.findall(r"[\w°]+", question) if len(word) > 1}
    def score(item: Difference) -> int:
        searchable = " ".join([
            item.explanation, item.affected, item.recommended_action,
            item.old.text if item.old else "", item.new.text if item.new else "",
            item.review_status, item.reviewer_note,
        ]).lower()
        return sum(token in searchable for token in tokens) + (2 if item.review_status != "未覆核" else 0)
    return sorted(differences, key=score, reverse=True)[:limit]


def local_chat_answer(question: str, context: list[Difference], language: str) -> str:
    if not context:
        return "找不到足以支持此問題的文件來源，請改以設備、程序或風險關鍵字提問。" if language == "繁中" else "No document evidence was found for this question. Try an equipment, procedure, or risk term."
    lines = []
    for item in context:
        source = item.new or item.old
        status = f"已人工覆核 ({item.review_status})" if item.review_status != "未覆核" else "尚未人工覆核"
        lines.append(f"- **{item.id}**（風險：{item.risk}，狀態：{status}）：{item.explanation} ｜ **可能影響：**{item.affected} ｜ **建議處置：**{item.recommended_action}（來源：PDF p.{source.page}）。")
    warning = "\n\n> ⚠️ **聲明：** 本回答依據比對證據整理，僅供作業草稿與提示，不構成正式工程或法規解釋。" if language == "繁中" else "\n\n> ⚠️ **Notice:** Answer is based on document evidence for draft guidance only and does not replace official engineering/regulatory approval."
    return "以下是可追溯的相關變更與證據：\n" + "\n".join(lines) + warning if language == "繁中" else "Traceable relevant evidence:\n" + "\n".join(lines) + warning

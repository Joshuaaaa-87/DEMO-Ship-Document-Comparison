from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from io import BytesIO
from typing import Iterable

from pypdf import PdfReader


SAFETY_TERMS = ("必須", "禁止", "警告", "危險", "壓力", "溫度", "bar", "mpa", "warning", "danger", "caution")
OBLIGATION_TERMS = ("必須", "應", "不得", "禁止", "建議", "每次", "每週", "每月")


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
    old: Source | None
    new: Source | None
    needs_review: bool = True
    review_status: str = "未覆核"
    reviewer_note: str = ""

    def asdict(self) -> dict:
        return asdict(self)


def extract_pages(file_bytes: bytes) -> list[Source]:
    reader = PdfReader(BytesIO(file_bytes))
    return [Source(page=index + 1, text=(page.extract_text() or "").strip()) for index, page in enumerate(reader.pages)]


def _lines(pages: Iterable[Source]) -> list[Source]:
    result = []
    for page in pages:
        for line in page.text.splitlines():
            clean = " ".join(line.split())
            if len(clean) > 12 and not clean.startswith("Fictional training"):
                result.append(Source(page.page, clean))
    return result


def _risk_and_reason(old: str, new: str) -> tuple[str, str, str]:
    content = f"{old} {new}".lower()
    numeric = bool(re.search(r"\b\d+(?:\.\d+)?\s?(?:°c|bar|mpa|%|hours?)\b", content, re.I))
    safety = any(term in content for term in SAFETY_TERMS)
    obligation_change = any(term in old + new for term in OBLIGATION_TERMS)
    if numeric and safety:
        return "High", "數值與安全相關條件改變，可能影響操作安全。", "高"
    if obligation_change:
        return "High", "程序義務、頻率或禁止性語意可能改變，需人工確認。", "中"
    if safety:
        return "Medium", "內容含安全相關詞彙，請確認是否影響程序。", "中"
    return "Low", "偵測到可追溯的文字或內容變更。", "高"


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
    return "；".join(found) if found else "待工程人員確認"


def compare_documents(old_pages: list[Source], new_pages: list[Source]) -> list[Difference]:
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
            old_value = old_item.text if old_item else ""
            new_value = new_item.text if new_item else ""
            risk, explanation, confidence = _risk_and_reason(old_value, new_value)
            differences.append(Difference(
                id=f"D{counter:02d}", change_type=change_type, risk=risk,
                confidence=confidence, explanation=explanation,
                affected=_affected(f"{old_value} {new_value}"), old=old_item, new=new_item,
            ))
            counter += 1
    return differences


def retrieve_context(question: str, differences: list[Difference], limit: int = 4) -> list[Difference]:
    tokens = {word.lower() for word in re.findall(r"[\w°]+", question) if len(word) > 1}
    def score(item: Difference) -> int:
        searchable = " ".join([
            item.explanation, item.affected, item.old.text if item.old else "", item.new.text if item.new else "", item.review_status, item.reviewer_note,
        ]).lower()
        return sum(token in searchable for token in tokens) + (2 if item.review_status != "未覆核" else 0)
    return sorted(differences, key=score, reverse=True)[:limit]


def local_chat_answer(question: str, context: list[Difference], language: str) -> str:
    if not context:
        return "找不到足以支持此問題的文件來源，請改以設備、程序或風險關鍵字提問。" if language == "繁中" else "No document evidence was found for this question. Try an equipment, procedure, or risk term."
    lines = []
    for item in context:
        source = item.new or item.old
        status = item.review_status if item.review_status != "未覆核" else "尚未人工覆核"
        lines.append(f"- {item.id}（{item.risk}，{status}）：{item.explanation} 來源：PDF p.{source.page}。")
    warning = "\n注意：本回答僅依已檢索的文件差異，不構成正式工程或法規解釋。" if language == "繁中" else "\nNote: This answer is limited to retrieved document differences and is not an engineering or regulatory interpretation."
    return "以下是可追溯的相關內容：\n" + "\n".join(lines) + warning if language == "繁中" else "Traceable relevant findings:\n" + "\n".join(lines) + warning


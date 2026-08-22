from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pymupdf

from .llm import llm_client
from .storage import Store, json_dump


SPACE_RE = re.compile(r"\s+")
VERSION_RE = re.compile(
    r"(?i)(?:\b(?:rev(?:ision)?|version|ver|v)|版本|版次)\s*[:._-]?\s*\d+(?:\.\d+)+"
)
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9])[-+]?\d+(?:[.,]\d+)?\s*(?:°\s*C|°\s*F|bar|kPa|MPa|Pa|Nm|N·m|kW|MW|V|A|mm|cm|m|kg|t|rpm|%|小時|分鐘|秒|天|週|月)?",
    re.IGNORECASE,
)
OBLIGATION_TERMS = {
    "必須", "應", "應當", "不得", "禁止", "建議", "可", "shall", "must",
    "should", "may", "required", "prohibited", "recommended",
}
SAFETY_TERMS = {
    "壓力", "溫度", "閥", "緊急", "安全", "危險", "火災", "防火", "隔離",
    "載重", "警報", "停機", "pressure", "temperature", "valve", "emergency",
    "safety", "hazard", "fire", "isolation", "alarm", "shutdown",
}


def normalize_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", text or "")
    value = value.replace("\u00ad", "").replace("\x00", "")
    return SPACE_RE.sub(" ", value).strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def truncate(text: str | None, length: int = 1200) -> str:
    value = normalize_text(text or "")
    return value if len(value) <= length else value[: length - 1] + "…"


def natural_title(old_text: str, new_text: str, kind: str) -> str:
    source = new_text if kind != "deleted" else old_text
    source = normalize_text(source)
    if not source:
        return {"added": "新增內容", "deleted": "刪除內容"}.get(kind, "內容變更")
    first = re.split(r"(?<=[。！？.!?])\s+|\n", source)[0]
    if len(first) > 56:
        first = first[:55] + "…"
    prefix = {"added": "新增：", "deleted": "刪除：", "modified": "修改："}.get(kind, "")
    return prefix + first


def term_set(text: str, terms: set[str]) -> set[str]:
    lowered = text.lower()
    return {term for term in terms if term.lower() in lowered}


def classify_difference(kind: str, old_text: str, new_text: str, page_confidence: float) -> dict[str, Any]:
    triggers: list[str] = []
    # Document revision labels such as v2.1 → v3.0 are metadata, not equipment values.
    old_numbers = set(NUMBER_RE.findall(VERSION_RE.sub("", old_text)))
    new_numbers = set(NUMBER_RE.findall(VERSION_RE.sub("", new_text)))
    old_obligations = term_set(old_text, OBLIGATION_TERMS)
    new_obligations = term_set(new_text, OBLIGATION_TERMS)
    safety = term_set(f"{old_text} {new_text}", SAFETY_TERMS)

    if old_numbers != new_numbers and (old_numbers or new_numbers):
        triggers.append("數值或單位變更")
    if old_obligations != new_obligations and (old_obligations or new_obligations):
        triggers.append("義務詞彙變更")
    if safety:
        triggers.append("安全相關詞彙")
    if kind in {"added", "deleted"}:
        triggers.append("整段新增或刪除")

    if "數值或單位變更" in triggers or "義務詞彙變更" in triggers:
        priority = "high"
    elif "安全相關詞彙" in triggers or kind in {"added", "deleted"}:
        priority = "medium"
    else:
        priority = "low"

    if page_confidence < 0.55:
        confidence = "low"
    elif page_confidence < 0.85:
        confidence = "medium"
    else:
        confidence = "high"

    explanation = {
        "high": "規則偵測到需要優先人工確認的數值、單位或義務詞彙變更。",
        "medium": "內容有結構性變更或包含安全相關詞彙，建議人工確認適用範圍。",
        "low": "目前未觸發高優先級規則，仍需確認是否屬排版或一般文字調整。",
    }[priority]
    return {
        "priority": priority,
        "confidence": confidence,
        "triggers": triggers,
        "system_explanation": explanation,
        "must_review": priority == "high" or confidence == "low",
    }


@dataclass
class Unit:
    text: str
    normalized: str
    page_number: int
    bbox: list[float] | None
    confidence: float


class ComparisonPipeline:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.ocr_language = os.getenv("PLIMSOLL_OCR_LANG", "eng+chi_tra")
        self.ocr_dpi = int(os.getenv("PLIMSOLL_OCR_DPI", "220"))
        self.minimum_text_chars = int(os.getenv("PLIMSOLL_MIN_TEXT_CHARS", "24"))

    @property
    def ocr_available(self) -> bool:
        return shutil.which("tesseract") is not None

    def extract_document(
        self,
        path: Path,
        side: str,
        session_id: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        pages: list[dict[str, Any]] = []
        issues: list[dict[str, Any]] = []
        document = pymupdf.open(path)
        if document.needs_pass:
            document.close()
            raise ValueError(f"{side} PDF 已加密，請先提供未加密版本")
        if document.page_count == 0:
            document.close()
            raise ValueError(f"{side} PDF 沒有頁面")
        if document.page_count > 600:
            document.close()
            raise ValueError("第一版單份 PDF 上限為 600 頁")

        jsonl_path = self.store.session_dir(session_id) / f"{side}.pages.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as jsonl:
            for index, page in enumerate(document):
                page_number = index + 1
                extraction_method = "pymupdf"
                confidence = 1.0
                textpage = None
                raw_text = page.get_text("text", sort=True)

                if len(normalize_text(raw_text)) < self.minimum_text_chars:
                    if self.ocr_available:
                        try:
                            textpage = page.get_textpage_ocr(
                                language=self.ocr_language,
                                dpi=self.ocr_dpi,
                                full=True,
                            )
                            raw_text = page.get_text("text", textpage=textpage, sort=True)
                            extraction_method = "ocr-tesseract"
                            confidence = 0.72 if len(normalize_text(raw_text)) >= self.minimum_text_chars else 0.35
                        except Exception as error:  # OCR errors vary by local language installation.
                            extraction_method = "ocr-failed"
                            confidence = 0.15
                            issues.append(
                                {
                                    "side": side,
                                    "page_number": page_number,
                                    "issue_type": "ocr_failed",
                                    "message": f"OCR 失敗：{str(error)[:180]}",
                                }
                            )
                    else:
                        extraction_method = "ocr-unavailable"
                        confidence = 0.1
                        issues.append(
                            {
                                "side": side,
                                "page_number": page_number,
                                "issue_type": "ocr_unavailable",
                                "message": "頁面沒有足夠文字層，且本機尚未安裝 Tesseract OCR。",
                            }
                        )

                block_values = page.get_text(
                    "blocks", textpage=textpage, sort=True
                ) if textpage else page.get_text("blocks", sort=True)
                blocks: list[dict[str, Any]] = []
                for block in block_values:
                    if len(block) < 7 or int(block[6]) != 0:
                        continue
                    block_text = normalize_text(str(block[4]))
                    if not block_text:
                        continue
                    blocks.append(
                        {
                            "bbox": [round(float(value), 2) for value in block[:4]],
                            "text": block_text,
                            "block_number": int(block[5]),
                        }
                    )

                text = "\n\n".join(block["text"] for block in blocks) or normalize_text(raw_text)
                if len(text) < self.minimum_text_chars and not any(
                    issue["side"] == side and issue["page_number"] == page_number for issue in issues
                ):
                    issues.append(
                        {
                            "side": side,
                            "page_number": page_number,
                            "issue_type": "insufficient_text",
                            "message": "頁面可提取文字不足，必須人工查看原始頁面。",
                        }
                    )
                    confidence = min(confidence, 0.35)

                try:
                    print_label = page.get_label() or str(page_number)
                except Exception:
                    print_label = str(page_number)
                record = {
                    "session_id": session_id,
                    "side": side,
                    "page_number": page_number,
                    "print_label": print_label,
                    "width": round(page.rect.width, 2),
                    "height": round(page.rect.height, 2),
                    "extraction_method": extraction_method,
                    "confidence": confidence,
                    "page_hash": sha256_bytes(text.encode("utf-8")),
                    "text": text,
                    "blocks": blocks,
                }
                pages.append(record)
                jsonl.write(json_dump(record) + "\n")
        document.close()
        return pages, issues

    @staticmethod
    def units_from_pages(pages: list[dict[str, Any]]) -> list[Unit]:
        units: list[Unit] = []
        for page in pages:
            if page["blocks"]:
                for block in page["blocks"]:
                    text = truncate(block["text"], 1800)
                    normalized = normalize_text(text).lower()
                    if len(normalized) < 3 or re.fullmatch(r"[-–—\d\s/]+", normalized):
                        continue
                    units.append(
                        Unit(
                            text=text,
                            normalized=normalized,
                            page_number=page["page_number"],
                            bbox=block.get("bbox"),
                            confidence=page["confidence"],
                        )
                    )
            elif page["text"]:
                units.append(
                    Unit(
                        text=truncate(page["text"], 1800),
                        normalized=normalize_text(page["text"]).lower(),
                        page_number=page["page_number"],
                        bbox=None,
                        confidence=page["confidence"],
                    )
                )
        return units

    @staticmethod
    def pair_replacements(old_units: list[Unit], new_units: list[Unit]) -> list[tuple[Unit | None, Unit | None]]:
        pairs: list[tuple[Unit | None, Unit | None]] = []
        remaining_new = set(range(len(new_units)))
        for old_unit in old_units:
            best_index = None
            best_score = 0.0
            for index in remaining_new:
                score = SequenceMatcher(
                    None, old_unit.normalized, new_units[index].normalized, autojunk=False
                ).ratio()
                if score > best_score:
                    best_score = score
                    best_index = index
            if best_index is not None and best_score >= 0.18:
                pairs.append((old_unit, new_units[best_index]))
                remaining_new.remove(best_index)
            else:
                pairs.append((old_unit, None))
        for index in sorted(remaining_new):
            pairs.append((None, new_units[index]))
        return pairs

    def build_differences(
        self,
        old_pages: list[dict[str, Any]],
        new_pages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        old_units = self.units_from_pages(old_pages)
        new_units = self.units_from_pages(new_pages)
        matcher = SequenceMatcher(
            None,
            [unit.normalized for unit in old_units],
            [unit.normalized for unit in new_units],
            autojunk=False,
        )
        pairs: list[tuple[Unit | None, Unit | None]] = []
        for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
            if tag == "equal":
                continue
            old_slice = old_units[old_start:old_end]
            new_slice = new_units[new_start:new_end]
            if tag == "replace":
                pairs.extend(self.pair_replacements(old_slice, new_slice))
            elif tag == "delete":
                pairs.extend((unit, None) for unit in old_slice)
            elif tag == "insert":
                pairs.extend((None, unit) for unit in new_slice)

        differences: list[dict[str, Any]] = []
        for index, (old_unit, new_unit) in enumerate(pairs[:800], start=1):
            old_text = old_unit.text if old_unit else ""
            new_text = new_unit.text if new_unit else ""
            if old_unit and new_unit:
                similarity = SequenceMatcher(
                    None, old_unit.normalized, new_unit.normalized, autojunk=False
                ).ratio()
                if similarity > 0.985:
                    continue
                kind = "modified"
                page_confidence = min(old_unit.confidence, new_unit.confidence)
            elif old_unit:
                kind = "deleted"
                page_confidence = old_unit.confidence
            else:
                kind = "added"
                page_confidence = new_unit.confidence if new_unit else 0.0

            classification = classify_difference(kind, old_text, new_text, page_confidence)
            differences.append(
                {
                    "id": f"D{len(differences) + 1:03d}",
                    "kind": kind,
                    "title": natural_title(old_text, new_text, kind),
                    "old_page": old_unit.page_number if old_unit else None,
                    "new_page": new_unit.page_number if new_unit else None,
                    "old_bbox": old_unit.bbox if old_unit else None,
                    "new_bbox": new_unit.bbox if new_unit else None,
                    "old_text": truncate(old_text),
                    "new_text": truncate(new_text),
                    **classification,
                    "recommended_action": "請對照原文、確認適用設備與實際作業影響。",
                    "llm_explanation": None,
                }
            )
        return differences

    def compare(self, session_id: str, old_path: Path, new_path: Path, use_llm: bool) -> None:
        try:
            old_pages, old_issues = self.extract_document(old_path, "old", session_id)
            new_pages, new_issues = self.extract_document(new_path, "new", session_id)
            differences = self.build_differences(old_pages, new_pages)

            model_used = None
            if use_llm and llm_client.enabled and differences:
                enrichments = llm_client.enrich_differences(differences)
                for difference in differences:
                    enrichment = enrichments.get(difference["id"])
                    if enrichment:
                        difference["llm_explanation"] = enrichment.get("explanation")
                        difference["recommended_action"] = (
                            enrichment.get("recommended_action") or difference["recommended_action"]
                        )
                model_used = llm_client.model

            self.store.replace_analysis(
                session_id,
                old_pages + new_pages,
                old_issues + new_issues,
                differences,
                model_used,
            )
        except Exception as error:
            self.store.mark_failed(session_id, str(error))
            raise


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

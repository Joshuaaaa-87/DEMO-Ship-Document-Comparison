from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class LLMClient:
    """Small OpenAI-compatible adapter used only for grounded semantic enrichment."""

    def __init__(self) -> None:
        groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.api_key = os.getenv("PLIMSOLL_LLM_API_KEY", "").strip() or groq_api_key
        self.provider = "groq" if groq_api_key and not os.getenv("PLIMSOLL_LLM_API_KEY") else "openai-compatible"
        default_model = "openai/gpt-oss-20b" if self.provider == "groq" else ""
        self.model = (
            os.getenv("PLIMSOLL_LLM_MODEL", "").strip()
            or os.getenv("GROQ_MODEL", "").strip()
            or default_model
        )
        default_base_url = (
            "https://api.groq.com/openai/v1"
            if self.provider == "groq"
            else "https://api.openai.com/v1"
        )
        self.base_url = (
            os.getenv("PLIMSOLL_LLM_BASE_URL", "").strip() or default_base_url
        ).rstrip("/")

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.model)

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "model": self.model or None,
            "provider": self.provider if self.enabled else "rules-only",
        }

    def _chat(self, messages: list[dict[str, str]], temperature: float = 0.1) -> str:
        if not self.enabled:
            raise RuntimeError("LLM 尚未設定")
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        with httpx.Client(timeout=90) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _parse_json(text: str) -> Any:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)

    def enrich_differences(self, differences: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
        if not self.enabled or not differences:
            return {}
        payload = [
            {
                "id": item["id"],
                "kind": item["kind"],
                "rule_priority": item["priority"],
                "triggers": item.get("triggers", []),
                "old_text": (item.get("old_text") or "")[:1200],
                "new_text": (item.get("new_text") or "")[:1200],
            }
            for item in differences[:40]
        ]
        system = (
            "你是船舶技術文件差異整理助手。只能根據輸入的新舊原文整理變更，"
            "不得自行斷言已造成事故、違法或必然風險。輸出純 JSON 陣列；每筆必須包含 "
            "id、explanation、recommended_action。recommended_action 應使用『建議人工確認』等保守措辭。"
        )
        content = self._chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ]
        )
        try:
            records = self._parse_json(content)
        except (json.JSONDecodeError, TypeError):
            return {}
        if not isinstance(records, list):
            return {}
        return {
            str(record.get("id")): {
                "explanation": str(record.get("explanation", ""))[:1200],
                "recommended_action": str(record.get("recommended_action", ""))[:800],
            }
            for record in records
            if isinstance(record, dict) and record.get("id")
        }

    def answer(self, question: str, context: dict[str, Any]) -> str:
        if not self.enabled:
            raise RuntimeError("LLM 尚未設定")
        differences = [
            {
                "id": diff["id"],
                "priority": diff["priority"],
                "title": diff["title"],
                "old_page": diff.get("old_page"),
                "new_page": diff.get("new_page"),
                "old_text": (diff.get("old_text") or "")[:700],
                "new_text": (diff.get("new_text") or "")[:700],
                "reviewed": diff.get("reviewed"),
            }
            for diff in context.get("differences", [])[:80]
        ]
        system = (
            "你是 Plimsoll 文件覆核助手。回答只能使用提供的差異資料，"
            "每個結論都要引用差異 ID 與頁碼。找不到證據時明確回答『目前資料不足』。"
            "你不能代替船長、主管或合格工程人員做最終安全判定。"
        )
        return self._chat(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"question": question, "differences": differences},
                        ensure_ascii=False,
                    ),
                },
            ],
            temperature=0.2,
        )


llm_client = LLMClient()

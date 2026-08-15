from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


def analyze_difference_with_llm(
    old_text: str,
    new_text: str,
    old_page: Optional[int],
    new_page: Optional[int],
    provider: str = "OpenAI",
) -> Optional[Dict[str, Any]]:
    """Analyze a single text difference using an LLM provider if API key is available.

    Returns structured analysis conforming to the spec schema:
    {
        "meaning_change": str,
        "risk_level": "High" | "Medium" | "Low",
        "confidence": "高" | "中" | "低",
        "affected_items": str,
        "recommended_action": str,
        "needs_human_review": bool,
        "evidence": str
    }
    If API key is missing or call fails, returns None (triggering rule-based fallback).
    """
    prompt = f"""你是一名資深船舶工程與安全品質審查專家。請分析以下兩版船舶技術文件的片段差異：

[舊版 (p.{old_page or 'N/A'})]:
{old_text or '(無對應舊版段落)'}

[新版 (p.{new_page or 'N/A'})]:
{new_text or '(無對應新版段落)'}

請以繁體中文 (台灣繁體) 進行分析，嚴格輸出 JSON 格式，不可包含 Markdown 標記以外的贅字。
JSON 格式規範如下：
{{
    "meaning_change": "詳細說明明確的文字、數值、程序或義務變更",
    "risk_level": "High" (若涉及壓力/溫度/安全/義務/關鍵數值/禁止條款) 或 "Medium" 或 "Low",
    "confidence": "高" 或 "中" 或 "低",
    "affected_items": "受影響的設備、零件或維修檢查程序名稱",
    "recommended_action": "給工程人員的具體處置或檢查建議",
    "needs_human_review": true,
    "evidence": "舊版 p.{old_page or '-'}: {old_text[:40]}... / 新版 p.{new_page or '-'}: {new_text[:40]}..."
}}
"""

    if provider.startswith("OpenAI"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                top_p=0.95,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
        except Exception:
            return None

    elif provider.startswith("Gemini"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.5,
                    "topP": 0.95,
                    "responseMimeType": "application/json",
                },
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception:
            return None

    elif provider.startswith("Groq"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        try:
            import urllib.request
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "top_p": 0.95,
                "response_format": {"type": "json_object"},
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                return json.loads(text)
        except Exception:
            return None

    return None

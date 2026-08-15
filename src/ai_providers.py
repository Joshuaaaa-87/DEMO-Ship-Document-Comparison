from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List, Optional


def call_llm(
    prompt: str,
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)",
    image_base64_old: Optional[str] = None,
    image_base64_new: Optional[str] = None,
) -> Optional[str]:
    """Orchestrate LLM calls prioritizing AWS Bedrock (Claude 3.5 Sonnet) or OpenAI (ChatGPT GPT-4o)."""

    # Priority 1: AWS Bedrock (Claude 3.5 Sonnet / Claude 3 Haiku)
    if "Bedrock" in provider or provider.startswith("AWS"):
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if aws_access_key and aws_secret_key:
            try:
                import boto3
                client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                )

                content = []
                if image_base64_old:
                    content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_base64_old}})
                if image_base64_new:
                    content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_base64_new}})
                content.append({"type": "text", "text": prompt})

                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2048,
                    "temperature": 0.5,
                    "top_p": 0.95,
                    "messages": [{"role": "user", "content": content}],
                })

                response = client.invoke_model(
                    body=body,
                    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                    accept="application/json",
                    contentType="application/json",
                )
                response_body = json.loads(response.get("body").read())
                return response_body["content"][0]["text"]
            except Exception:
                pass  # Fallback to OpenAI if AWS credentials not set or call fails

    # Priority 2: OpenAI ChatGPT (GPT-4o / GPT-4o-mini / Vision)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            messages_content: List[Dict[str, Any]] = []

            if image_base64_old:
                messages_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64_old}"}})
            if image_base64_new:
                messages_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64_new}"}})
            messages_content.append({"type": "text", "text": prompt})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": messages_content}],
                temperature=0.5,
                top_p=0.95,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception:
            pass

    return None


def analyze_difference_with_llm(
    old_text: str,
    new_text: str,
    old_page: Optional[int],
    new_page: Optional[int],
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)",
) -> Optional[Dict[str, Any]]:
    prompt = f"""你是一名資深船舶工程與工安審查專家。請分析以下兩版船舶技術手冊的差異：

[舊版 (p.{old_page or 'N/A'})]:
{old_text or '(無對應舊版段落)'}

[新版 (p.{new_page or 'N/A'})]:
{new_text or '(無對應新版段落)'}

請以繁體中文 (台灣繁體) 進行精準解讀，嚴格輸出 JSON 格式：
{{
    "meaning_change": "詳細說明明確的文字、數值、程序或義務變更",
    "risk_level": "High" (若涉及壓力/溫度/安全/義務/關鍵數值/禁止條款) 或 "Medium" 或 "Low",
    "confidence": "高",
    "affected_items": "受影響的設備、零件號碼或維修檢查程序名稱",
    "recommended_action": "給工程人員的具體處置或檢查建議",
    "term_tags": ["專業術語/零件號標籤", "如 CP-120"],
    "ratio_highlights": ["X/Y 數值或極限比例標示", "如 8/10 bar, 3/5 頻率"]
}}
"""
    raw_res = call_llm(prompt, provider=provider)
    if raw_res:
        try:
            return json.loads(raw_res)
        except Exception:
            return None
    return None


def extract_structure_with_llm(
    page_text: str,
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)",
) -> Optional[Dict[str, Any]]:
    """Use AI model to eliminate heading/subtitle extraction errors with high precision."""
    prompt = f"""你是一名技術文件結構標註專家。請精準解析以下頁面文字的主標題、副標題、版本號與適用範圍，避免抓錯標題：

[頁面文字]:
{page_text}

請嚴格輸出 JSON：
{{
    "main_title": "精準主標題",
    "subtitle": "副標題/章節標題",
    "version": "版本號如 v1.0",
    "section_code": "S1000D DMC 碼或章節號",
    "applicability": "適用船型或設備"
}}
"""
    raw_res = call_llm(prompt, provider=provider)
    if raw_res:
        try:
            return json.loads(raw_res)
        except Exception:
            return None
    return None


def analyze_image_diff_with_llm(
    image_base64_old: str,
    image_base64_new: str,
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)",
) -> Optional[Dict[str, Any]]:
    """Use Multimodal Vision AI to analyze visual engineering drawing diffs."""
    prompt = """請視覺比對這兩張船舶工程水路/電路圖快照，辨識圖中管線、閥門位置、閥門開度、流量數字 (如 X/Y 標示) 與關鍵組件標號之差異。

請嚴格輸出 JSON：
{
    "has_visual_change": true,
    "visual_explanation": "詳細說明圖表管線、閥門與數值變更",
    "changed_elements": ["新增迴流閥門 V-102", "流量指標 8 bar"]
}
"""
    raw_res = call_llm(prompt, provider=provider, image_base64_old=image_base64_old, image_base64_new=image_base64_new)
    if raw_res:
        try:
            return json.loads(raw_res)
        except Exception:
            return None
    return None


def generate_mindmap_and_slides_with_llm(
    differences: List[Dict[str, Any]],
    provider: str = "AWS Bedrock (Claude 3.5 Sonnet)",
) -> Optional[Dict[str, Any]]:
    """Synthesize 5-slide Demo presentation deck & Mindmap tree from version differences."""
    prompt = f"""依據以下船舶技術文件變更明細，生成「Demo Day 5 頁簡報大綱」與「變更樹心智圖 (Mindmap JSON)」：

[差異數據 (前 10 筆)]:
{json.dumps(differences[:10], ensure_ascii=False)}

請嚴格輸出 JSON：
{{
    "presentation_slides": [
        {{"slide": 1, "title": "簡報標題", "bullets": ["要點 1", "要點 2"]}},
        {{"slide": 2, "title": "核心工安變更摘要", "bullets": ["要點 1", "要點 2"]}},
        {{"slide": 3, "title": "設備與SOP影響評估", "bullets": ["要點 1", "要點 2"]}},
        {{"slide": 4, "title": "工程師行動清單與簽核", "bullets": ["要點 1", "要點 2"]}},
        {{"slide": 5, "title": "價值主張與維護效益", "bullets": ["要點 1", "要點 2"]}}
    ],
    "mindmap_tree": {{
        "name": "船舶技術文件改版總覽",
        "children": [
            {{"name": "高風險工安條文", "children": [{{"name": "出口溫度 85°C ➔ 80°C"}}]}},
            {{"name": "設備保養頻率", "children": [{{"name": "每月 ➔ 每週保養"}}]}},
            {{"name": "零件料號更新", "children": [{{"name": "CP-100 ➔ CP-120"}}]}}
        ]
    }}
}}
"""
    raw_res = call_llm(prompt, provider=provider)
    if raw_res:
        try:
            return json.loads(raw_res)
        except Exception:
            return None
    return None

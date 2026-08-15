# AI 船舶技術文件版本差異 Agent

以 Streamlit 建立的第一版 Demo：比較兩份 PDF、保留每筆變更的頁碼與原文、以可解釋規則標示安全風險，並提供人工覆核、檢索式聊天與 HTML 報告。

## 啟動

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

初次使用可先執行 `python scripts/generate_demo_pdfs.py` 產生 `data/demo/` 下的兩份 6 頁合成 PDF。

## 模型供應商

介面預設依序顯示 OpenAI、Gemini、Bedrock、Groq。第一版在沒有金鑰時以本機可解釋規則運作；外部模型設定會由 `.env` 讀取，且不會提交到 Git。


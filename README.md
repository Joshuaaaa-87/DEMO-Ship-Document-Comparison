# AI 船舶技術文件版本差異 Agent (Ship Document Version Difference Agent)

以 Streamlit 建立的 AI 代理展示原型：比較兩份船舶技術文件 (PDF)、保留 100% 可追溯之頁碼與段落原文 (S1000D 結構理念對齊)、標示重大安全風險、提供 4 大驗收情境關卡（Normal、Exception 掃描圖檔警示、Missing Info 元數據補件、Human Control 人工覆核防誤匯出）、RAG 檢索式問答聊天與獨立 HTML 審查報告。

## 快速啟動

```bash
# 1. 建立虛擬環境與安裝套件
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. 產生 6 頁合成 Demo PDF (若尚未產生)
.venv/bin/python3 scripts/generate_demo_pdfs.py

# 3. 啟動 Web 應用程式
.venv/bin/streamlit run app.py
```

## 自動化測試驗證

本專案內建 Playwright 端對端測試腳本，完整驗證核心比對、4 大驗收情境與瀏覽器 UI 互動：

```bash
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py
```

## AI 供應商與推論設定

- 支援適配器：OpenAI (GPT-4o), Gemini, Amazon Bedrock, Groq。
- 模型推論參數：`Temperature = 0.5`, `Top P = 0.95` (恪守低隨機性與事實對齊規範)。
- 金鑰設定：在 `.env` 中設定 `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY` 或 `AWS_REGION`；若未設定 API Key，系統將自動以可解釋之精準規則引擎運作，確保 Demo 在無 Key 狀態下依然可完美展演。

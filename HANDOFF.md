# 開發交接：AI 船舶技術文件版本差異 Agent

## 目前狀態

已建立可啟動的 Streamlit 第一版原型與兩份 6 頁虛構 Demo PDF。尚未完成瀏覽器端對端驗證、外部 AI API 呼叫與 GitHub Issue 建立。

## 已完成

- `app.py`：繁中／英文切換、PDF 上傳、Demo 載入、差異指標、可追溯差異列、人工覆核、來源雙欄 PDF 檢視、檢索式本機聊天與 HTML 報告下載。
- `src/comparison.py`：PDF 頁面文字提取、行級 diff、數值／義務／安全詞風險規則、影響設備推定與來源檢索。
- `scripts/generate_demo_pdfs.py`：建立兩份 6 頁虛構冷卻系統文件（v1.0、v1.1）。
- `data/demo/Main_Engine_Cooling_v1.0.pdf`、`data/demo/Main_Engine_Cooling_v1.1.pdf`：已生成。
- `.gitignore`、`requirements.txt`、`README.md`：已建立；`.venv` 已安裝 Streamlit、pypdf、reportlab。

## 已驗證

```text
python -m py_compile app.py src/comparison.py scripts/generate_demo_pdfs.py  # pass
PDF pages: 6/6
Detected differences: 25
High-risk candidates: 2
```

## 尚未完成 / 風險

- 尚未用 Playwright 啟動 Streamlit、點擊「載入 Demo」、測試人工覆核、聊天與 HTML 下載。
- `pdftoppm` 於 sandbox 顯示 Fontconfig 無寫入快取的警告，輸出大量雜訊；先以 `pdfinfo` 與 `pypdf` 驗證頁數、文字與生成流程。
- AI provider 選單與固定證據格式已預留，但尚未串 OpenAI／Gemini／Bedrock／Groq API；目前以規則 + 檢索式本機聊天實作，避免沒有 API key 時失效。
- 真實掃描 PDF／複雜表格／章節重排的 OCR 與語意對齊尚未實作，必須標示低信心並人工確認。

## 下一步

1. 依 `webapp-testing` skill：先執行 `python /Users/caspertseng/.codex/skills/webapp-testing/scripts/with_server.py --help`，再用它啟動 `.venv/bin/streamlit run app.py --server.port 8501`。
2. 撰寫最小 Playwright 測試，點擊「載入 6 頁合成 Demo」，確認指標、差異列、聊天輸入與 HTML 下載按鈕出現。
3. 修正測試發現的 UI 問題。
4. 若使用者提供 API key，以 `.env` 讀取，先實作 OpenAI adapter；統一回傳 `meaning_change`、`risk_level`、`confidence`、`affected_items`、`recommended_action`、`needs_human_review`、`evidence`。後續依同一介面新增 Gemini、Bedrock、Groq。
5. 完成後執行 `git status`，不要提交或 push，除非使用者要求。

## 啟動

```bash
.venv/bin/streamlit run app.py
```

## 需求決策

- UI：Streamlit、NotebookLM 式來源閱讀、繁中預設且可切英文。
- 模型優先序：OpenAI > Gemini > Bedrock > Groq。
- Chat：優先引用人工覆核；無覆核時引用原始 PDF 與系統差異，證據不足須明確說明。
- 報告：重點指標置頂、詳細來源置後、可下載獨立 HTML。
- 安全：語意判讀是候選警示，不取代工程／法規正式解釋。

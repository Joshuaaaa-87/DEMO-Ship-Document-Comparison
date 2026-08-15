# 開發交接：AI 船舶技術文件版本差異 Agent

## 目前狀態

已完成所有剩餘開發任務、四種驗收情境關卡（Normal、Exception 掃描圖檔警示、Missing Info 元數據補件、Human Control 人工覆核防誤匯出）與 Playwright 端對端自動化測試。

## 已完成

- `app.py`：繁中／英文切換、PDF 上傳、Demo 載入、文件元數據顯示、差異指標、可追溯差異列、人工覆核（選擇狀態與筆記）、來源雙欄 PDF 檢視、RAG 檢索式聊天問答、掃描 PDF 警告、版本缺失手動補填與包含審查警示標章之 HTML 報告下載。
- `src/comparison.py`：PDF 頁面文字提取、行級與段落級 diff、掃描頁檢測 (`detect_scanned_pages`)、元數據解析 (`extract_metadata`)、數值／義務／安全詞風險規則、影響設備推定、建議處置與來源檢索。
- `src/ai_providers.py`：實作 OpenAI, Gemini, Bedrock, Groq 語意分析適配器，設定 `Temperature=0.5` 及 `Top P=0.95` 事實對齊參數，支援環境變數 API Key 讀取與無 Key 時之優雅降級。
- `scripts/generate_demo_pdfs.py`：建立兩份 6 頁虛構冷卻系統技術文件（v1.0、v1.1）。
- `scripts/run_e2e_tests.py`：使用 Playwright 測試框架建立 5 大自動化測試關卡，涵蓋核心比對邏輯、掃描頁警示、元數據補填、HTML 報告警告與無頭瀏覽器 UI 互動驗證。
- `.gitignore`、`requirements.txt`、`README.md`、`HANDOFF.md`：依最新規格更新完備。

## 已驗證

```text
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py

--- [1/5] Core Comparison Engine: 25 differences found, High-risk candidates flagged. (PASSED)
--- [2/5] Exception Path: Scanned image PDF warning triggered. (PASSED)
--- [3/5] Missing Info Path: Incomplete metadata version input triggered. (PASSED)
--- [4/5] Human Control Path: Unreviewed High-risk export warning guard verified. (PASSED)
--- [5/5] Playwright Browser UI Automation: Headless Chromium end-to-end verified. (PASSED)

🎉 ALL 5 E2E TEST SUITES PASSED CLEANLY!
```

## 啟動與測試

```bash
# 啟動 Web 應用程式
.venv/bin/streamlit run app.py

# 執行端對端自動化測試
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py
```

## 需求與規格對齊決策

- **4 大驗收情境 (Acceptance Criteria)**：
  - **Normal Path**：5-10 頁技術文件上傳，100% 精準追溯頁碼與段落原文。
  - **Exception Path**：圖像/掃描頁偵測並跳出 OCR 與人工雙重校對警示。
  - **Missing Info Path**：文件標題/版本號缺漏時跳出手動指定與補填提示。
  - **Human Control Path**：人工覆核勾選關卡，未完成 High 項目覆核時於 UI 及 HTML 報告顯眼警示。
- **AI 供應商優先序**：OpenAI > Gemini > Bedrock > Groq（支援 `.env` API Key；無 Key 時自動使用精準規則與可追溯對齊引擎）。
- **推論參數設定**：`Temperature = 0.5`, `Top P = 0.95`（恪守低隨機性與結構事實嚴謹度）。

# 開發交接：AI 船舶技術文件版本差異 Agent (React + FastAPI 全新架構)

## 目前狀態

已成功將系統重構升級為 **Vite + React + Tailwind CSS (前端 SPA)** 與 **Python FastAPI (後端)** 架構，並強化了 **勝過 NotebookLM 之關鍵差異對照**、**安品主管 vs 第一線維修工程師雙角色視圖**、**3~5 版多版本演進時間軸矩陣** 與 **自訂 DOCX 審查報告匯出**。

## 已完成

- `frontend/`：使用 Vite + React + TypeScript + Tailwind CSS 建立現代化深色 UI。
  - `Header.tsx`：角色彩色切換器 (🛡️ 安品主管 vs 🔧 維修工程師)、分頁切換 (單比對視圖 / 3~5 版時間軸 / 競品差異對照)、模型選擇器。
  - `NotebookLMDifferentiator.tsx`：清晰對照卡片，凸顯「S1000D 100% 頁碼原文對照」、「工安數值自動標紅」、「強制人工審查簽核軌跡」與「多版本橫向演進矩陣」等勝過 NotebookLM 之核心價值。
  - `ManagerDashboard.tsx`：安品主管視圖（工安 KPI 指標、待簽核重大項目警示、主管行動處置清單、Audit Trail 歷史合規紀錄）。
  - `EngineerDashboard.tsx`：第一線工程師視圖（逐筆可追溯差異卡片、數值高亮、建議處置、簽核下拉選單、筆記輸入、掃描檔 OCR 警示）。
  - `MultiVersionTimeline.tsx`：3~5 版橫向多版本演進時間軸矩陣 (v1.0 ➔ v1.1 ➔ v1.2 ➔ v2.0)。
  - `ReportExporter.tsx`：自訂 Word (.docx) 與 HTML/PDF 格式審查報告靜態與即時匯出。
- `backend/`：Python FastAPI 後端 API 服務 (`backend/main.py`) 與 `backend/docx_exporter.py`。
  - `/api/compare`: 雙 PDF 上傳比對。
  - `/api/demo-data`: 載入 6 頁合成 Demo。
  - `/api/chat`: RAG 自然語言問答。
  - `/api/export-docx`: 靜態/動態 DOCX 審查報告生成。
  - 靜態掛載 `./frontend/dist` 展現純 Single-Port 部署能力。
- `scripts/run_e2e_tests.py`：Playwright 端對端自動化測試套件，涵蓋 5 大驗收測試關卡。

## 已驗證

```text
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py

--- [1/5] Core Comparison Engine: 25 differences found, High-risk candidates flagged. (PASSED)
--- [2/5] Exception Path: Scanned image PDF warning triggered. (PASSED)
--- [3/5] Missing Info Path: Incomplete metadata version input triggered. (PASSED)
--- [4/5] Human Control Path: Unreviewed High-risk export warning guard verified. (PASSED)
--- [5/5] Playwright React + FastAPI Browser UI Automation: Headless Chromium end-to-end verified. (PASSED)

🎉 ALL 5 E2E TEST SUITES PASSED CLEANLY!
```

## 啟動與測試

```bash
# 1. 啟動 FastAPI 後端 + React 前端 (Port 8000)
.venv/bin/python3 -m uvicorn backend.main:app --port=8000 --reload

# 2. 獨立開發前端 (Port 5173，具 HMR 即時熱重載)
cd frontend && npm run dev

# 3. 執行 Playwright 端對端測試
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py
```

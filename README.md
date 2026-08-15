# AI 船舶技術文件版本差異 Agent (Ship Document Version Difference Agent)

本專案升級重構為 **Vite + React + Tailwind CSS (前端 SPA)** 與 **Python FastAPI (後端)** 架構。

## 🌟 關鍵核心價值 (勝過 NotebookLM 之四大優勢)

1. **100% 精準 S1000D 頁碼與原文段落雙欄對照**：絕無 LLM 幻覺，每筆變更皆可點擊即時查閱 PDF 原頁原文。
2. **工安數值門檻自動標紅警示 (High Risk)**：自動辨識壓力 (bar/MPa)、溫度 (°C) 變化與義務詞彙變更。
3. **角色化專屬視圖 (Role-Based Dashboards)**：
   - **🛡️ 安品/工程主管**：高階工安 KPI 指標、待簽核重大項目警示、行動處置清單 (Action Items) 與 Audit Trail 歷史合規軌跡。
   - **🔧 第一線維修工程師**：詳細 SOP 流程變更、設備料號對比、雙欄 PDF 閱讀器與覆核簽核筆記。
4. **3~5 版多版本橫向演進時間軸矩陣 (Multi-Version Matrix)**：一頁橫覽條文在 v1.0 ➔ v1.1 ➔ v1.2 ➔ v2.0 跨版本之演進。
5. **自訂範本 DOCX & PDF 報告匯出**：生成含公司標頭、審查時間、舊/新版本、簽核欄位與完整明細之 Word (.docx) / PDF 報告。

## 🚀 快速啟動

```bash
# 1. 建立虛擬環境與安裝依賴
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. 構建前端生產環境產物 (已於 frontend/dist 生成)
cd frontend && npm install && npm run build && cd ..

# 3. 啟動 FastAPI 服務 (Port 8000 提供全系統 API 與 React 介面)
.venv/bin/python3 -m uvicorn backend.main:app --port=8000 --reload
```

## 🧪 自動化測試驗證

```bash
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py
```

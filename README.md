# AI 船舶技術文件版本差異 Agent (Ship Document Version Difference Agent)

本專案重構升級為 **Vite + React + Tailwind CSS (前端 SPA)** 與 **Python FastAPI (後端 API)** 架構，專為高風險船舶工程、S1000D 技術手冊、海事產險保條與鋼船驗船規範設計。

---

## 🌟 關鍵核心價值 (勝過 NotebookLM 之四大優勢)

1. **100% 精準 S1000D 頁碼與原文段落雙欄對照**：絕無 LLM 幻覺，每筆變更皆可點擊即時查閱 PDF 原頁原文。
2. **工安數值門檻自動標紅警示 (High Risk)**：自動辨識壓力 (bar/MPa)、溫度 (°C) 變化與義務詞彙變更。
3. **角色化專屬視圖 (Role-Based Dashboards)**：
   - **🛡️ 安品/工程主管**：高階工安 KPI 指標、待簽核重大項目警示、行動處置清單 (Action Items) 與 Audit Trail 歷史合規軌跡。
   - **🔧 第一線維修工程師**：詳細 SOP 流程變更、設備料號對比、雙欄 PDF 閱讀器與覆核簽核筆記。
4. **3~5 版多版本橫向演進時間軸矩陣 (Multi-Version Matrix)**：一頁橫覽條文在 v1.0 ➔ v1.1 ➔ v1.2 ➔ v2.0 跨版本之演進。
5. **自訂範本 DOCX & PDF 報告匯出**：生成含公司標頭、審查時間、舊/新版本、簽核欄位與完整明細之 Word (.docx) / PDF 報告。

---

## 📂 專案目錄結構 (Project Directory Structure)

```text
DEMO-Ship-Document-Comparison/
├── backend/                  # Python FastAPI 後端 API 服務
│   ├── main.py               # REST API 端點、檔案上傳中轉與 static 掛載
│   └── docx_exporter.py      # 自訂範本 Word (.docx) 審查報告生成引擎
├── frontend/                 # Vite + React + TypeScript + Tailwind CSS 前端應用
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx                 # 頂端列 (角色切換器、Nav Tabs、Model Selector)
│   │   │   ├── ManagerDashboard.tsx       # 🛡️ 安品主管審查視圖 (工安 KPI、Audit Trail)
│   │   │   ├── EngineerDashboard.tsx      # 🔧 第一線維修工程師視圖 (SOP 差異對照、簽核)
│   │   │   ├── MultiVersionTimeline.tsx   # 📊 3~5 版橫向多版本演進時間軸對照矩陣
│   │   │   ├── SlidesMindmapViewer.tsx    # 📽️ Demo Day 5 頁簡報與變更樹心智圖預覽器
│   │   │   ├── FloatingChatDrawer.tsx     # 🚢 右下角浮動小船對話按鈕與右滑抽屜
│   │   │   ├── NotebookLMDifferentiator.tsx # 勝過 NotebookLM 之關鍵優勢對照卡片
│   │   │   └── ReportExporter.tsx         # 自訂 DOCX/PDF 報告匯出觸發器
│   │   ├── types.ts                       # 前端 TypeScript 型別定義
│   │   ├── App.tsx                        # React 主應用組裝
│   │   ├── main.tsx                       # React 進入點
│   │   └── index.css                      # Tailwind CSS 主樣式檔
│   └── dist/                 # Vite 生產環境靜態產物 (已於發布前構建)
├── src/                      # 核心比對與 AI 階層調度模組
│   ├── comparison.py         # S1000D 頁碼段落對照引擎、工安數值高紅規則與 RAG 檢索
│   └── ai_providers.py       # AI 階層調度器 (AWS Bedrock Claude 3.5 & OpenAI GPT-4o)
├── scripts/                  # 腳本工具與自動化測試
│   ├── run_e2e_tests.py      # Playwright 5 大關卡端對端 E2E 自動化測試腳本
│   └── generate_demo_pdfs.py # 6 頁合成 Demo PDF 數據生成腳本
├── data/                     # 數據與規格文件庫
│   ├── demo/                 # 6 頁合成 Demo PDFs (v1.0 & v1.1)
│   └── specs/                # 專案參考規範、講義與大型鋼船規則 PDFs (歸檔庫)
├── HANDOFF.md                # 系統交接說明與測試啟動指令
├── README.md                 # 本說明文件
├── requirements.txt          # Python 套件依賴需求檔 (FastAPI, python-docx, openai, boto3...)
└── .env.example              # 環境變數 API Key 設定範本
```

---

## 🚀 快速啟動

```bash
# 1. 安裝套件依賴
.venv/bin/pip install -r requirements.txt

# 2. 構建前端生產環境產物 (已於 frontend/dist 生成)
cd frontend && npm install && npm run build && cd ..

# 3. 啟動 FastAPI 服務 (Port 8000 提供全系統 API 與 React 介面)
.venv/bin/python3 -m uvicorn backend.main:app --port=8000 --reload
```

開啟 `http://127.0.0.1:8000` 即可體驗完整功能。

---

## 🧪 自動化測試驗證

```bash
PYTHONPATH=. .venv/bin/python3 scripts/run_e2e_tests.py
```

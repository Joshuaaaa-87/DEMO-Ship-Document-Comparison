# Plimsoll 船舶技術文件版本差異工作台

第一個可運作的本機迭代版。前端是單一 HTML，後端使用 FastAPI，處理流程為：

`PyMuPDF 文字提取 → 低文字量頁面選擇性 OCR → 頁面 JSONL → 規則式差異候選 → 選配 LLM 語意整理 → 人工覆核 → 報表匯出`

## 啟動

需要 Python 3.12+ 與 Tesseract OCR（建議安裝 `eng`、`chi_tra` 語言資料）。

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

開啟 <http://127.0.0.1:8000/plimsoll-workbench-v1.html>。首頁 `/` 也會顯示同一個工作台。

## 在不同主機執行（建議）

主機只要安裝 Docker，即可把 Python、PyMuPDF、Tesseract 與繁中 OCR 語言包一起啟動：

```bash
cp .env.example .env
docker compose up --build
```

開啟主機的 `http://主機位址:8000/`。資料會保存在 Docker volume `plimsoll-data`。

## LLM（選配）

沒有設定 LLM 時，文件提取、OCR、規則比對、人工覆核與匯出仍可完整使用。若要啟用 OpenAI-compatible LLM 語意整理，先設定：

```bash
export PLIMSOLL_LLM_API_KEY="your-key"
export PLIMSOLL_LLM_MODEL="your-model"
export PLIMSOLL_LLM_BASE_URL="https://api.openai.com/v1"
```

如果使用 Groq，只需要在 `.env` 設定：

```bash
GROQ_API_KEY=your-groq-key
GROQ_MODEL=openai/gpt-oss-20b
```

系統會自動使用 `https://api.groq.com/openai/v1`；Groq Key 不會送到瀏覽器，也不應提交至 Git。
直接使用本機 Python 啟動時也會自動讀取專案根目錄的 `.env`；修改 Key 或模型後需重新啟動服務。

其他可調整項目：`PLIMSOLL_OCR_LANG`（預設 `eng+chi_tra`）、`PLIMSOLL_OCR_DPI`（預設 `220`）與 `PLIMSOLL_DATA_DIR`。

## 資料與匯出

- SQLite 與原始 PDF 儲存在 `.plimsoll/`，此資料夾不納入 Git。
- 每次比對都保存新舊版頁面級 JSONL。
- 支援 PDF、Excel、HTML 與差異 JSONL 匯出。
- 高優先差異與文字提取覆蓋缺口未經人工確認前，報告標記為「修訂草稿」。

## 測試

```bash
.venv/bin/python tests/test_integration.py
```

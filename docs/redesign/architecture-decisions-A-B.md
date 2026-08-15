# Plimsoll — 架構決策 A / B（可直接併入 ui-spec.md §9）

> 決策者：系統架構師　·　依據：已驗證需求摘要 v3、`Plimsoll_UI設計評論_v1.md` §1.3 / §2.2
> **儲存策略：local-first，DB 為可選上游。** 無 DB 時本機檔案為真相來源；接上 DB 後可把本機資料灌入。
> 現況基線（反面參考）：`src/comparison.py` 的 `Difference.review_status` 為可覆寫字串、`Source.page` 為單一 PDF 頁、`_risk_and_reason()` 門檻寫死、`/api/vision-diff` 回未標記假資料。

---

## v1 前提（已與需求方確認，2026-08-15）

- **使用情境：單人單機**（單一覆核人、單一機器）。JSONL 單寫入者足夠，v1 不需 DB→local pull。
- **真相來源：本機永遠為主**，DB 永遠是下游鏡像；同步**單向 push（local→DB）**，不做 pull。
- **本輪交付：只更新規格**（ui-spec §9 #19–24、§3.4 ④），不動程式。決策落 `claude/plimsoll-architecture-decisions-…` 分支，**不 push、不碰 `main`／`codex/260815`**。
- **C2（nice-to-have，暫不做）**：PDF 原檔在本機的暫存**僅 P3「原始 PDF」模式才需要**，標為 nice-to-have；**v1 不做自動清理**，原檔留在使用者指定的本機資料夾由使用者自理。
- **仍待決（不阻擋本輪）**：JSONL 每行的 `prev_hash`/`prev_event_id` 在單人單機＋前綴錨點下屬冗餘，可留作 belt-and-suspenders 或日後精簡。

---

## 核心觀念：事件日誌＝同步協定

因為稽核軌跡採 **append-only、事件不可變、每筆帶唯一 `event_id`**（§21），同步到任何上游只是：
「讀出本機尚未確認的事件 → 依 `event_id` idempotent upsert 到上游」。
**沒有合併衝突**（不會發生本機與 DB 對 D01 各執一詞），只有「上游少了 e-0003…e-0007，補上去」。這讓 local↔DB 同步從一個大工程縮成一個 for-loop。

---

## 儲存架構：兩層 + 一個 Gateway

```
┌─ 應用（FastAPI） ─────────────────────────────────────────────┐
│                     StorageGateway                             │
│  append_event(e):  ① 一律先寫 LocalStore ＝ commit 點          │
│                    ② 若 SyncTarget 健康 → best-effort 寫穿      │
│  flush_pending():  讀 last_synced 之後的事件 → idempotent 灌入  │
└───────────────┬───────────────────────────────┬───────────────┘
                │                               │
      Layer 1： LocalStore（永遠在，離線可用）    Layer 2： SyncTarget（可選、可插拔）
      · review_events.jsonl  (append-only ★)     · 介面：is_connected / ingest_events
      · session.json / differences.json          · 實作：Postgres / MySQL / SQLite檔
      · config/*.json                            ·       / 雲端 API / Google Sheet(受#5限)
      · sync_state.json (可變 sidecar)           · v1 可只留介面 + 一個參考 adapter
      ＝ 真相來源                                 ＝ 下游鏡像，非第二真相來源
```

**規則**：LocalStore 的寫入才算「已提交」；SyncTarget 寫失敗，事件仍安全躺在本機並標為未同步。DB **永遠是下游鏡像**，不是第二個真相來源——這保住 #7 輕量可轉向：換任何 DB＝換一個 adapter，核心不動。

### 三態 tag（由 `sync_state.json` 推導，非稽核資料）

| tag | 條件 |
|---|---|
| `本機` | 未設定 SyncTarget，或從未同步 |
| `未同步` | 有 SyncTarget，且本機存在 > `last_synced_event_id` 的事件 |
| `已同步` | `last_synced_event_id` ＝ 本機最後事件 |

```json
// sessions/<id>/sync_state.json —— 這個檔可覆寫（操作性中繼資料，不是稽核軌跡）
{ "target": "postgresql://…(redacted)", "last_synced_event_id": "e-0002", "synced_at": "2026-08-15T03:41:00Z", "pending": 1 }
```

> 注意：同步進度寫在**獨立可變** sidecar，**絕不**回頭改 `review_events.jsonl`——稽核日誌永遠只增不改。

---

## 三種本機格式的定位（釐清）

使用者列的 google sheet / excel / txt，實際分屬不同層：

| 格式 | 定位 | 原因 |
|---|---|---|
| **txt / JSONL** | **本機真相來源**（Layer 1） | 唯一能真 append、離線、零相依、可 grep/diff |
| **Excel .xlsx / CSV** | **匯出鏡像**（唯讀視圖） | xlsx 整檔重寫、開檔即鎖，不能當 append-only 真相來源；但適合稽核人用 Excel 開 |
| **Google Sheet** | **上游 SyncTarget 之一**（Layer 2） | 需網路＋OAuth，非本機；本質是遠端，屬「DB 那一側」。受 #5 限制，v1 不建，但介面留槽 |

---

## §9 新增條目（建議編號 19–23）

| # | 決定 |
|---|---|
| 19 | **P0–P4 儲存範圍（local-first，DB 可選上游）**：稽核軌跡寫入本機 append-only JSONL（`review_events.jsonl`），工作階段／差異各存一份一次性 JSON——**無 DB 亦可完整運作**，本機檔案即真相來源。設定 DB 連線且可達時，本機事件以 `event_id` idempotent 灌入 DB（下游鏡像，非第二真相來源）；未連線或失敗則保留於本機並標 `未同步`。表格檢視以匯出 `.xlsx`/`.csv`（唯讀）滿足。Google Sheet／雲端屬上游 SyncTarget 之一，受 #5 限制 v1 不建、僅留介面。`localStorage` 只存 UI 偏好。理由：需求 #2 要求不可覆寫遺失＋ #7 輕量可轉向，local-first 保證離線可用，事件日誌讓 DB 同步免衝突。 |
| 20 | **核准角色與可調分級規則（檔案版）**：覆核人拆 `reviewer_name`＋`approval_role_code`。角色以 `config/approval_roles.json` 承載（非寫死 enum），種子 `DPA/TECH_SUPT/FLEET_MGR/OTHER`，可增列免改程式；`OTHER` 另存 `custom_role_label`。分級門檻以版本化 `config/rulesets/v{N}.json` 承載，調門檻＝新增版本檔、比對凍結 `ruleset_version`；核准權限以 `config/approval_policies/v{N}.json` 承載。同步時 config 亦隨事件一併灌入 DB。覆核與簽核經事件關聯此二者，並存 `approval_role_label_snapshot` 快照。 |
| 21 | **稽核軌跡採 append-only 事件檔，且兼任同步協定**：覆核狀態為 `review_events.jsonl` 唯增長事件流之投影（讀檔 fold），非可變欄位；改判＝追加凌獨行。每筆帶唯一 `event_id` 使上游 upsert idempotent、forward-only、免衝突。**防竄改採「凍結前綴 hash 錨點」**：格式與規則嚴格定義（每行固定 schema），讀檔時對已凍結前綴 `[0, offset)` 取 SHA-256 快照存於**別處**（DB 優先，離線退本機 `.integrity/`）；灌 DB 前重算前綴 hash 比對，不一致＝歷史區疑遭手改 → **告警並略過該 session 之 ingest**（隔離、不灌入、待人工）。同步進度存獨立可變 `sync_state.json`，**永不**回改稽核日誌。寫入單寫入者序列化。骨幹落 **P0**。 |
| 22 | **雙頁碼對映與 data_origin 一級欄位**：頁碼為 `{pdf_page, print_label, label_source}`，取自 PDF PageLabels（可非數字；抓不到 `NULL` 且 `label_source=unknown`，不猜測）。API 回傳帶 `data_origin ∈ {computed, ai_inferred, demo_seed}`，真實 session 禁未標記寫死值。 |
| 23 | **SyncTarget 契約（可插拔上游）**：定義 `SyncTarget` 介面（`is_connected()`／`ingest_events(events)`／`ingest_config(...)`），LocalStore 為 commit 點，DB 為 best-effort／延後 flush 之下游鏡像。三態 tag（`本機`／`未同步`／`已同步`）由 `sync_state.json` 推導。v1 交付**介面 + 一個參考 adapter**（建議 SQLAlchemy Core，同一份程式以連線字串接 SQLite 檔／Postgres／MySQL），使「連線後把本機資料存入 DB」端到端可驗，且不綁定特定 DB 品牌（#7）。 |
| 24 | **DB 連線不得影響啟動，且 UI 須明示連線狀態**：(a) 啟動路徑**只讀本機檔案**，不得有任何 DB 呼叫；DB 連線一律**延遲、背景、帶短逾時**探測，設定錯誤／不可達／逾時皆**降級為本機模式**，永不阻塞或崩潰。(b) 介面須清楚顯示「是否已連上資料庫」：於**設定 → 資料來源**新增「資料庫同步」狀態區（沿用 §3.4 ③ AI 模型的狀態列綠／灰燈樣式），顯示連線狀態、待同步筆數、手動同步鈕與連線設定；並於全域保留一顆小狀態點。**此為新增前端工作，需併入 ui-spec §3.4 並待 UI/UX 確認**（見下方條文草案）。 |

---

## 本機檔案配置（P0 落地）

```
data/store/                         # 可由「設定 → 資料來源」指定的本機資料夾
├── config/
│   ├── approval_roles.json         # 核准角色（可增列）
│   ├── rulesets/v1.json            # 分級門檻；調門檻＝新增 v2.json（immutable）
│   └── approval_policies/v1.json   # 角色 × 可核准最高風險級
├── sessions/
│   └── <session_id>/
│       ├── session.json            # 一次寫入
│       ├── differences.json        # 比對後一次寫入，immutable（含雙頁碼＋AI 初判）
│       ├── review_events.jsonl     # ★ append-only 稽核軌跡（唯一成長檔）
│       └── sync_state.json         # 可覆寫 sidecar：同步進度（非稽核資料）
└── exports/
    └── <session_id>-audit.xlsx     # 匯出鏡像（唯讀）
```

---

## `review_events.jsonl` 一行一事件（append-only，兼同步單位）

```jsonl
{"event_id":"e-0001","session_id":"s-8f2","difference_id":"D01","event_type":"AI_INITIAL","ai_risk_at_time":"High","ai_confidence_at_time":"高","ruleset_version":"v1","human_verdict":null,"reviewer_name":null,"approval_role_code":null,"created_at":"2026-08-15T03:30:00Z","prev_event_id":null,"prev_hash":null,"hash":"a1b2…"}
{"event_id":"e-0002","session_id":"s-8f2","difference_id":"D01","event_type":"HUMAN_REVIEW","ai_risk_at_time":"High","ruleset_version":"v1","human_verdict":"CONFIRMED","risk_override":null,"reviewer_name":"陳○○","approval_role_code":"TECH_SUPT","approval_role_label_snapshot":"安全品質主管（Technical Superintendent）","reviewer_note":"已核對新版 p.4","created_at":"2026-08-15T03:35:12Z","prev_event_id":"e-0001","prev_hash":"a1b2…","hash":"c3d4…"}
```

**投影（現況）＋安全寫入＋同步**：

```python
_lock = asyncio.Lock()

async def append_event(session_id, event: dict):        # ① 一律先落地本機＝commit
    line = json.dumps(event, ensure_ascii=False)
    async with _lock:
        with open(events_path(session_id), "a", encoding="utf-8") as f:
            f.write(line + "\n"); f.flush(); os.fsync(f.fileno())
    if sync_target and sync_target.is_connected():       # ② best-effort 寫穿；失敗不影響 commit
        try: sync_target.ingest_events([event]); mark_synced(session_id, event["event_id"])
        except Exception: pass                            #    → 留待 flush_pending 補

def flush_pending(session_id):                            # 接上 DB 後手動/自動觸發
    anchor = load_anchor(session_id)                      # 別處存的「已確認前綴」錨點（DB 優先，離線退本機 .integrity/）
    raw = open(events_path(session_id), "rb").read()
    # ① 驗證凍結前綴未遭手改（append-only：[0,offset) 永不再變）
    if anchor and sha256(raw[:anchor["offset"]]) != anchor["prefix_sha256"]:
        alert("完整性驗證失敗：歷史稽核區疑遭手改", session_id)
        return "QUARANTINED"                              # 告警並略過，不灌入 DB，待人工
    # ② 只灌入錨點之後的新事件；格式/規則不符也告警略過
    pending = parse_jsonl(raw[anchor["offset"]:]) if anchor else parse_jsonl(raw)
    validate_schema(pending)
    sync_target.ingest_events(pending)                    # 依 event_id idempotent upsert
    save_anchor(session_id, offset=len(raw), prefix_sha256=sha256(raw))  # 更新錨點＝新前綴
```

### 完整性驗證（tamper-evidence）— 凍結前綴 hash 錨點

- **格式/規則先寫死**：每行固定 JSONL schema，讀檔即 `validate_schema()`，手改破壞結構直接被抓。
- **錨點存「別處」**：`(offset, prefix_sha256)`。**首選存 DB**（每次成功 ingest 後由伺服器記住「上次到 offset N、前綴 hash＝H」，本機端編輯器動不到）；**離線期**退而存 `data/store/.integrity/<session_id>.json`（與日誌不同子樹，防隨手改）。
- **與 append-only 相容**：只 hash 已凍結前綴 `[0, offset)`，合法追加只長尾端、不動前綴；故前綴 hash 恆定，改到前綴＝竄改。
- **不一致的處置**：`告警 + 略過 ingest + 隔離該 session`，本機日誌**照原樣保留**（它本身就是稽核證據，只是標記「完整性待查」），由人工判定，系統不自動刪改。

---

## 上游 DB schema（可選 SyncTarget；接上時才用）

> 與本機事件同構；`review_events` 主鍵＝`event_id` 讓重放 idempotent。DB 是鏡像，非真相來源。

```sql
CREATE TABLE review_events (
  event_id                     TEXT PRIMARY KEY,   -- idempotent 重放鍵
  session_id                   TEXT NOT NULL,
  difference_id                TEXT NOT NULL,
  event_type                   TEXT NOT NULL,      -- AI_INITIAL / HUMAN_REVIEW / RISK_OVERRIDE / EXPORT_SIGNOFF
  ai_risk_at_time              TEXT,
  ruleset_version              TEXT,
  human_verdict                TEXT,               -- CONFIRMED / TRACK / REJECTED / FALSE_POSITIVE
  risk_override                TEXT,
  reviewer_name                TEXT,
  approval_role_code           TEXT,
  approval_role_label_snapshot TEXT,
  reviewer_note                TEXT,
  created_at                   TEXT NOT NULL,
  prev_event_id                TEXT,
  hash                         TEXT
);
CREATE TABLE sessions    ( session_id TEXT PRIMARY KEY, title TEXT, old_doc_json TEXT, new_doc_json TEXT, ruleset_version TEXT, created_at TEXT, status TEXT );
CREATE TABLE differences ( session_id TEXT, difference_id TEXT, change_type TEXT, old_pdf_page INT, old_print_label TEXT, new_pdf_page INT, new_print_label TEXT, page_label_source TEXT, old_text TEXT, new_text TEXT, ai_risk TEXT, ai_confidence TEXT, ai_explanation TEXT, ai_trigger_rule TEXT, affected TEXT, recommended_action TEXT, ruleset_version TEXT, data_origin TEXT, PRIMARY KEY (session_id, difference_id) );
CREATE TABLE approval_roles    ( code TEXT PRIMARY KEY, label_zh TEXT, label_en TEXT, is_active INT, sort_order INT, is_system_seed INT );
CREATE TABLE rulesets          ( version TEXT PRIMARY KEY, rules_json TEXT, note TEXT, created_at TEXT );
CREATE TABLE approval_policies ( ruleset_version TEXT, approval_role_code TEXT, max_risk_can_approve TEXT, PRIMARY KEY (ruleset_version, approval_role_code) );
```

---

## config 檔（取代寫死 enum 與 `_risk_and_reason()`）

`config/approval_roles.json`
```json
[
  { "code": "DPA",       "label_zh": "DPA（Designated Person Ashore）", "label_en": "Designated Person Ashore", "is_active": true, "sort_order": 10, "is_system_seed": true },
  { "code": "TECH_SUPT", "label_zh": "安全品質主管",                     "label_en": "Technical Superintendent",   "is_active": true, "sort_order": 20, "is_system_seed": true },
  { "code": "FLEET_MGR", "label_zh": "船隊經理",                         "label_en": "Fleet Manager",              "is_active": true, "sort_order": 30, "is_system_seed": true },
  { "code": "OTHER",     "label_zh": "其他",                             "label_en": "Other",                      "is_active": true, "sort_order": 99, "is_system_seed": true }
]
```

`config/rulesets/v1.json`
```json
{
  "version": "v1",
  "safety_terms":     ["必須","禁止","警告","危險","壓力","溫度","bar","mpa","高於","低於","限值"],
  "obligation_terms": ["必須","應","不得","禁止","建議","每次","每週","每月","定期"],
  "rules": [
    { "id": "numeric_safety",  "priority": 10, "when": { "numeric_change": true, "safety_terms": true },
      "then": { "risk": "High",   "confidence": "高", "rationale": "數值與安全條件變更（壓力／溫度／極限參數）", "recommended_action": "停用舊版對應檢查表，通知工程人員並重新簽核" } },
    { "id": "obligation_plus", "priority": 20, "when": { "obligation_change": true, "any_of": ["safety_terms","numeric_change"] },
      "then": { "risk": "High",   "confidence": "高", "rationale": "作業程序／頻率／禁止性語意變更，需品保人員人工覆核", "recommended_action": "更新 SOP 流程並重新訓練維修工程人員" } },
    { "id": "obligation_only", "priority": 30, "when": { "obligation_change": true },
      "then": { "risk": "Medium", "confidence": "中", "rationale": "程序義務或維修頻率改變，需人工確認", "recommended_action": "調整定期保養排程與紀錄表" } },
    { "id": "safety_only",     "priority": 40, "when": { "safety_terms": true },
      "then": { "risk": "Medium", "confidence": "中", "rationale": "內容含安全關鍵詞，建議人工覆核", "recommended_action": "工程主管雙重確認" } },
    { "id": "default",         "priority": 999, "when": {},
      "then": { "risk": "Low",    "confidence": "高", "rationale": "一般文字或說明變更", "recommended_action": "更新技術手冊檔案存檔" } }
  ]
}
```

`config/approval_policies/v1.json`
```json
{ "ruleset_version": "v1", "policies": { "DPA": "High", "TECH_SUPT": "High", "FLEET_MGR": "Medium", "OTHER": "Low" } }
```

> 文案限制（#8）：`rationale`／`recommended_action` 禁「版次混淆導致事故」類因果斷言。
> 資料來源限制（#5）：詞庫僅通用工安詞，不得內建 DNV/LR/ABS 規範文字；`data/specs/` 船級社 PDF 不進種子或 RAG 語料。

---

## 前端條文草案（待 UI/UX 確認，擬併入 ui-spec.md §3.4 資料來源）

> 對應決定 #24。沿用 §3.4 ③「AI 模型」既有的狀態列綠/灰燈樣式，不新增視覺語彙。

**設定 → ④ 資料來源 → 新增「資料庫同步」區塊**

| 元件 | 規格 |
|---|---|
| 連線狀態列 | 綠燈「已連線 · PostgreSQL@host（或 SQLite 檔）」／灰燈「未連線 · 資料僅存本機」／琥珀燈「連線中…」／紅燈「連線失敗（原因）」。**啟動時預設灰燈**，背景探測完成才轉燈 |
| 待同步計數 | 「本機 N 筆待同步」；N=0 時顯示「已全部同步」 |
| 手動同步鈕 | 「立即同步到資料庫」；未連線時 disabled；同步中顯示進度與可取消 |
| 完整性告警 | 若 flush 偵測到某 session 完整性驗證失敗，此處紅字列出「M 筆因完整性待查已略過」，點擊展開清單，導向人工處置（不自動刪改） |
| 連線設定 | 連線字串／檔案路徑輸入 + 「測試連線」；Key/密碼型欄位只存瀏覽器工作階段，比照 §3.4 ③ API Key 規範，不寫入原始碼或版控 |

**全域小狀態點**
- TopBar 齒輪或既有儲存位置 tag 旁，放一顆 4px 狀態點（綠/灰/琥珀/紅），hover 顯示「資料庫：已連線／未連線」。P0–P4 主流程仍以單一「本機」呈現（決定 #19），此點只反映「有沒有接上 DB」，不改動既有三欄佈局。

**啟動與降級行為（前端可感知）**
- 首屏永遠可用（本機模式），不等待 DB。
- DB 探測為背景非阻塞；失敗只把狀態列轉灰/紅並允許稍後重試，**不彈錯誤中斷操作**。
- 「未連線」時，所有覆核/匯出功能照常運作，資料落本機並標 `未同步`。

> 待確認項：小狀態點的擺放位置（齒輪旁 vs. tag 旁）、是否需要在左欄列頂沿用 `未同步` 提示條。以上不影響後端資料模型，可由 UI/UX 獨立定案。

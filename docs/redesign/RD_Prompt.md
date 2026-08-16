你是負責實作「Plimsoll — 船舶技術文件版本差異 Agent」的軟體工程師。這是全新開發（無可信任的既有基線）。在寫任何程式碼之前，你必須先讀懂並整合以下輸入，其中「已驗證需求摘要 v4」優先權最高：

1. 命題與工作包：船舶技術文件版本差異_Agent_工作包.html
2. UI/UX 最終設計稿：ui-mockup-v3.2.html（僅供畫面參考，不需要再改設計）
3. 架構決策：architecture-decisions-A-B.md（已併入 ui-spec.md §9 #19–32）
4. 已驗證需求摘要 v4（貼於下方）

<validated_summary_v4>
F1：ui-mockup-v3.2.html 為最終定案設計稿；architecture-decisions-A-B.md §19–30 已可視為正式規格。
A1（已驗證）：三態儲存 tag（本機／未同步／已同步）＋ Drive 獨立為來源連線類型，UI 已證實可行。
A2（已驗證）：核准角色 config 化結構（DPA/TECH_SUPT/FLEET_MGR/OTHER）不需重畫版面即可容納。
Q1（已答）：全域 DB 連線狀態點放 TopBar 齒輪旁。
Q2（已答）：左欄不做「未同步」全欄橫幅；只在完整性驗證失敗時標記該列。
Q3（已答）：§28 2D 影響視圖維持 Someday，不在本輪範圍。
Risk 1（已修正）：核准角色改名「船舶技術監督」，與登入角色「安全品質主管」不再撞名。
Risk 2（已修正）：舊「遠端」tag 已全數清除，三態術語全文一致。
Risk 3（已收斂）：完整性告警的 P0 範圍動作＝下載原始日誌／標記已知悉，不做自動修復，不做完整調查指派流程。
Risk 4（未決，非開發行動）：OQ3 訪談輪機長／技術主管尚未排定，核心痛點急迫性仍未經產業驗證，屬最高風險項，架構與功能都要維持輕量可轉向。
</validated_summary_v4>

【本輪開發範圍】
- 只實作 P0–P4（骨架、上傳、對話主線、DiffCard 覆核、匯出攔截），對應 ui-spec.md §8。
- 例外可提前做：色盲友善色盤、離線自架字型、三態儲存 tag 的本機端（本機 JSONL 為真相來源，DB 為選用下游鏡像，見 §19/§21/§23）。
- 禁止現在動工：RWD 斷點、字型自選完整介面、視覺差異比對像素管線（P8）、2D 影響視圖（§28，Someday）、多版本矩陣（P9）、Google Drive 實際串接（P7，僅畫面可見入口即可，不用真的接 OAuth）。

【資料模型硬性規則（依 architecture-decisions-A-B.md）】
- 稽核軌跡：`review_events.jsonl`，append-only、每行固定 schema、每筆帶唯一 `event_id`；覆核狀態是事件流投影，不是可變欄位。
- 完整性驗證：凍結前綴 SHA-256 錨點；驗證失敗＝告警＋隔離該 session（不刪改、不自動修復），對應畫面⑨的「下載原始日誌／標記已知悉」兩個動作。
- 雙頁碼：`{pdf_page, print_label, label_source}`，抓不到就 `NULL` 且 `label_source=unknown`，不猜測。
- 核准角色：`reviewer_name` + `approval_role_code`（來自 `config/approval_roles.json`，可增列，種子 DPA/TECH_SUPT/FLEET_MGR/OTHER），UI 顯示用 `approval_role_label_snapshot`，且顯示時要用畫面⑤修正後的措辭（船舶技術監督），不要照抄舊的「安全品質主管」。
- 分級門檻：版本化 `config/rulesets/v{N}.json`，調門檻＝新增版本檔，比對凍結 `ruleset_version`，不可寫死在程式邏輯裡。
- 資料來源：僅本機檔案 + 自製合成文件；不得使用/索引 DNV/LR/ABS 等船級社規範。
- 假資料三態鐵則：所有 API 回傳帶 `data_origin ∈ {computed, ai_inferred, demo_seed}`，真實 session 不可出現未標記的寫死值。

【文案規則】
禁止「版次混淆導致事故」類因果斷言；一律用「確保執行者拿到正確、現行、完整的技術資料」。

【邊界】
不串接企業正式系統、不修改正式程序、不控制設備；分支一律在 `codex/260815`，不碰 `main`。PyMuPDF（AGPL）僅限於本 demo/非閉源商用場景使用，日後閉源商用化需另購授權。

【開始實作前，你必須先用繁體中文回覆】
1. 200 字內重述本輪（P0–P4）的 Business Thesis、Primary User、Critical Moment；
2. Confirmed（F）／Assumed（A）／Missing（Q）／Risk 四類清單，明確標出 Risk 4（OQ3 未驗證）為最高風險，且不因為它未解決就阻擋開發，只需保持架構輕量可轉向；
3. 最多五個需要我優先決定的問題；
然後停下來等待我回覆，不要直接開始寫程式碼。

【確認後的實作方式】
- 依 P0→P4 順序逐步進行，每階段開始前先提出小步計畫（元件、檔案異動、對應 AC、測試方式、commit 訊息）。
- 完成每個可測切片後，回報：Changed、Why、Tested、Not Yet Done、Risks、Next、Version。
- 涉及後端資料模型（雙頁碼、覆核稽核軌跡、分級規則、核准角色）時，嚴格依 architecture-decisions-A-B.md 的既定結構，不要自行改變。
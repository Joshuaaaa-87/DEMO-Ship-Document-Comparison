# Tasks

## Active

- [ ] **軟體工程師開場確認** - 用 Opus 4.8 跑「開始實作前的重述＋F/A/Q/Risk 清單」（prompt 已含摘要 v4 + Risk 1–3 收尾結果），等待人工確認後才進入 P0

## Waiting On

- [ ] **OQ3：訪談輪機長／技術主管**（Risk 4，最高風險，非開發行動）- 驗證核心痛點急迫性，架構已預留「輕量可轉向」但不應無限期擱置，建議盡快排定
- [ ] **OQ1：分級量化門檻** - 待企業訪談確認；已有可調規則的檔案結構（config/rulesets/v{N}.json），確認後直接寫入 v1.json 即可，不影響架構
- [ ] **OQ5：Google Drive／遠端同步的企業資料政策** - v1 僅畫面可見入口，不接真實 OAuth；政策確認後才定案 P7 實際串接
- [ ] **船級社規範（DNV/LR/ABS）使用書面同意** - 若未來要用作正式資料來源或 RAG 語料，需取得書面同意；v1 語料白名單已硬性排除

## Someday

- [ ] P5：RWD 斷點與底部分頁、左欄排序／拖曳
- [ ] P6：字型系統完整介面、比對高亮完整自訂色票
- [ ] P7：Google Drive 實際串接（OAuth、唯讀 Picker）— 待 OQ5 政策確認
- [ ] P8：視覺差異比對（PyMuPDF 光柵化 + 像素 diff + OCR 分層 + LLM 語意解讀，見 architecture-decisions-A-B.md §26）
- [ ] P9：多版本矩陣、簡報／心智圖真實資料串接
- [ ] §28：2D 影響視圖（component_ref + SFI 編碼 + SVG 高亮）— 待具體客戶需求＋component_ref 真實資料管線出現才啟動，3D 更後延
- [ ] §30：RAG 預留位置實作（語料白名單已定，介面已留槽，尚未實作）
- [ ] 完整性驗證失敗的完整調查指派流程（P0 僅做「下載原始日誌／標記已知悉」兩個最小動作）

## Done

- [x] ~~UI/UX 顧問審查~~ (2026-08-15) - 產出 Plimsoll_UI設計評論_v1.md，13 項發現
- [x] ~~修正 mockup A 類項目~~ (2026-08-15) - 產出 ui-mockup-v3.html
- [x] ~~架構師審查~~ (2026-08-15) - 產出 architecture-decisions-A-B.md（§19–32），已併入 ui-spec.md
- [x] ~~UI/UX 第二輪（回補架構師待確認事項）~~ (2026-08-15) - 產出 ui-mockup-v3.1.html：三態 tag 落地、資料庫同步設定區塊、確認 2D 影響視圖維持 Someday
- [x] ~~Risk 1–3 收尾修正~~ (2026-08-15) - 產出 ui-mockup-v3.2.html：核准角色改名去除歧義、清除全部殘留「遠端」tag、完整性告警補上 P0 最小處置動作

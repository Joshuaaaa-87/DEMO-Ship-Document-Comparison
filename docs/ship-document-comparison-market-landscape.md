# 船舶與海運文件比對市場：國際及臺灣競品研究

> 最後資料查核：2026-08-15  
> 研究範圍：船舶與船員證書、提單（Bill of Lading, B/L）、商業發票、裝箱單、原產地證明、港口支出帳單及 IHM 文件的擷取、交叉比對、真偽驗證與合規管理。  
> 注意：本文所稱「前十名」是將搜尋結果去重，排除政府查驗入口、新聞文章及虛構示範系統後，依商業相關度排列；不是個人化搜尋引擎排名的絕對名次。

## 結論摘要

國際上確實存在商業化的船舶與海運文件比對服務，而且可分成三條不同賽道：

1. **跨文件一致性比對：**比較提單、商業發票、裝箱單、原產地證明、契約或第三方證書的欄位是否一致。
2. **文件對外部資料驗證：**把文件聲明的船舶、航程、港口、公司及貨物資料與 AIS 航跡、實際靠港、船舶所有權及制裁名單交叉驗證。
3. **船舶／船員證書驗真與維護：**確認證書是否由船級社或政府核發、是否有效、是否完成必要簽註，以及是否即將到期。

臺灣已經有「跨報關文件比對」及「IHM 船舶文件維護」業者，但截至本次查核，公開市場上未發現一家臺灣純 SaaS 同時整合「多文件 AI 比對、AIS／制裁資料驗證及船舶證書管理」。這是依公開搜尋所得的市場觀察，不代表所有未公開銷售或客製專案都不存在。

## 搜尋與篩選方法

主要搜尋概念包括：

- `台灣 船舶 文件 比對 驗證 公司 船舶證書 電子驗證`
- `台灣 海運 提單 文件 自動化 審核 公司`
- `maritime vessel document verification software certificates company`
- `shipping document comparison AI bill of lading document automation company`

納入條件：

- 有可驗證的公司官網、產品頁、官方合約、定價頁或年度報告；
- 明確處理船舶、船員、海運、報關或國際貿易文件；
- 具有文件擷取、欄位比對、外部資料驗證、證書驗真或持續合規管理功能；
- 是可商業採購的產品或服務。

排除項目：

- 僅提供政府公共查驗、沒有對外商業模式的平台；
- 只談論技術但沒有商業產品的新聞、論文或社群文章；
- 虛構的展示環境。例如搜尋結果中的 Atlantis Ship Registry 是 Oceans HQ 用於教育與訓練的示範系統，不是一家真實船舶登記公司；
- 沒有明確海運文件應用的一般 OCR 工具。

## 前十個相關商業結果

| 排名 | 業者／地區 | 文件比對或驗證方法 | 獲利／收費模式 | 解決的使用者痛點 |
|---|---|---|---|---|
| 1 | **Windward／以色列、英國** | 以 GenAI 擷取 B/L、原產地證明等文件，再與 AIS、實際靠港、航程、船舶所有權、制裁／風險資料及貨櫃里程碑交叉驗證。若文件聲稱的港口實際未靠泊，系統會標示差異並提供解釋及稽核軌跡。 | 企業級年度 SaaS 或 API 訂閱。官方年報指出，價格依使用者數、地理範圍、功能、合約期、服務等級及 Web／API 交付方式決定。 | 偽造原產地、制裁規避、走私、關稅逃漏、人工調查太慢，以及貨物放行與資金流延誤。參考：[Document Validation](https://windward.ai/solutions/document-validation/)、[AI-Automated Document Validation 發布資訊](https://windward.ai/news/windward-launches-ai-automated-document-validation-to-streamline-trade-documents-against-real-world-maritime-activity/)、[官方年度報告的商業模式](https://investors.windward.ai/wp-content/uploads/2024/04/Annual-Report-Windward-2023.pdf) |
| 2 | **TradDocs／盧森堡、韓國** | 比較契約與 B/L，或以 B/L 為基準檢查 Invoice、Packing List、原產地證明及第三方證書；比對日期、櫃號、封條、船名、港口、當事人、重量與數量等欄位，並支援 API。 | Freemium SaaS：Starter 免費版每月 10 次 inspection；Basic 每月 20 次；Pro 為無限次，Basic／Pro 金額需洽詢，官網標示年繳省 20%；另有 Production 與 Sandbox API。 | 多份文件逐欄人工比對、漏件、日期或重量不一致，以及單一錯誤造成的交易損失。參考：[產品功能](https://www.traddocs.com/)、[官方定價](https://www.traddocs.com/pricing)、[API 文件](https://docs.traddocs.com/introduction)、[公司對使用者痛點的說明](https://www.traddocs.com/company) |
| 3 | **力新國際 NewSoft／臺灣** | 以 AI-OCR 擷取商業發票、B/L、Packing List，交叉比較重點欄位是否一致，再將資料送入後端或 ERP；包含旋轉、傾斜、梯形、裁切及去雜點等影像前處理。 | 銷售 API、單機版及企業軟體產品，也提供建置、數位化、系統整合與顧問服務；報關文件方案沒有公開價格，採洽詢報價。 | 進口報關前必須逐份建檔、核對並重複登打 ERP，造成耗時、人力不足及登打錯誤。參考：[AI-OCR 報關文件比對](https://www.newsoft.com.tw/ocr-service/)、[進口報關流程與解法](https://www.newsoft.com.tw/latest_news/%E5%8A%9B%E6%96%B0%E8%B2%A8%E7%89%A9%E9%80%B2%E5%8F%A3%E5%A0%B1%E9%97%9C%E5%96%AE%E6%93%9A%E8%BE%A8%E8%AD%98-%E5%8A%A0%E9%80%9F%E8%B2%A8%E7%89%A9%E5%A0%B1%E9%97%9C%E6%B5%81%E7%A8%8B%E7%9A%84%E9%80%B2/)、[官方產品與交付形式](https://www.newsoft.com.tw/) |
| 4 | **Marcura DA-Desk／杜拜、國際市場** | 比較港口預估及最終支出帳單（PDA／FDA）、發票、公告費率、客戶協議、折扣與歷史靠港成本；利用 1,800 多項規則找出重複發票、異常成本、費率差異及未套用折扣。 | 企業訂閱、專家 managed service 及 VMS 整合的混合模式；官方說明存在 subscription pricing 與 managed support，但未公開標準金額。 | 港口費用外漏、重複或不合理收費、漏掉環保／頻率折扣、帳單審核慢，以及稽核證據不足。參考：[DA-Desk 驗證方法](https://www.da-desk.com/abm/)、[企業服務與商業模式](https://marcura.com/why-marcura/da-desk-enterprise-control)、[驗證規則與歷史成本 FAQ](https://marcura.com/resources/faqs) |
| 5 | **Bol.ai／荷蘭** | 專門擷取 B/L，也能讀取 Invoice、Packing List 及 CMR；驗證 ISO 6346 貨櫃檢查碼與欄位合理性，輸出 JSON、CSV 或 API，並讓使用者逐欄覆核。較偏向「擷取＋欄位驗證」，不是完整的外部航跡驗證。 | Starter 為每月 €19 加每份文件 €0.49；Professional 為每月 €79 加每份文件 €0.29；另有 €49／100 份文件的免訂閱套裝。 | 不同船公司版型造成大量重打、掃描品質不一、貨櫃號碼錯誤，以及資料無法直接送進 TMS／ERP。參考：[產品、驗證方法及官方定價](https://bol.ai/) |
| 6 | **Expedock／美國** | 以 AI 擷取 B/L、Invoice、Packing List、AWB 等文件，執行 AP 發票與帳單 reconciliation、例外處理，並寫入 CargoWise、Magaya 或其他 TMS；同時提供人工 BPO。 | 混合 SaaS 與服務模式。正式合約以 SOW 決定費用，包含月訂閱、月結及合約自動續約；另銷售 fully managed staffing／BPO，未公開現行標準價。 | 文件輸入量增加就必須擴編、發票對帳複雜、供應商付款延誤、毛利資料不即時，以及純 OCR 無法處理例外。參考：[產品](https://www.expedock.com/)、[官方服務與訂閱合約](https://www.expedock.com/master-services-agreement)、[BPO 服務](https://www.expedock.com/bpo/logistics) |
| 7 | **Shipamax／WiseTech CargoWise／英國、澳洲** | 以 ML 自動分類 PDF、掃描、圖片及 email，不需逐一建立 OCR 模板；將資料轉成統一 schema 後，直接送入 CargoWise、ERP 或 TMS。 | Shipamax 於 2022 年被 WiseTech 收購，目前主要嵌入 CargoWise。2025 年起 CargoWise Value Packs 改採每一物流工作／交易計價，取消標準席次及雲端費。 | 重複輸入、re-key 錯誤、文件與 TMS 分離、資料完整性不足，以及缺乏即時例外處理。參考：[Shipamax 方法](https://shipamax.com/freight-forwarders/)、[官方收購說明](https://www.wisetechglobal.com/news/wisetech-global-acquires-industry-leading-data-entry-automation-business-shipamax/)、[CargoWise 現行交易計價](https://www.wisetechglobal.com/news/wisetech-global-launches-cargowise-value-packs-introducing-substantial-new-product-capabilities-and-simplified-billing/) |
| 8 | **DNV／挪威；臺灣有據點** | 發行帶有數位簽章及 Unique Tracking Number（UTN）的電子證書，讓港口、船東等透過 UTN、Approval Finder 或數位簽章確認證書真實性與有效狀態；只驗證 DNV 自己簽發的文件。 | 客戶按商業訂單購買驗船、認證、文件審查及驗證服務，DNV 開立發票；公開查驗入口是發證服務的信任層，未見對查驗者獨立收費。 | 假冒 DNV 證書、紙本無法即時確認、港口查驗時間長，以及船上與岸端持有不同版本。參考：[證書驗真方式](https://www.dnv.com/maritime/certification-authentication/)、[電子證書與 UTN](https://www.dnv.com/maritime/electronic-certificates/user-guide-and-faq/)、[商業訂單流程](https://maritime.dnv.com/DocumentApprovalHelp/CMC_Orders_for_Product_Certification_-_-Verification_%28CMC_-_VMC%29.html) |
| 9 | **Oceans HQ／英國** | 向船旗國及海事主管機關提供船舶、船員、檢驗、電子證書系統；第三方可利用 QR Code 或文件控制碼驗證核發狀態。其 Atlantis Ship Registry 是教學示範，不是真實船籍公司。 | B2G／B2B SaaS 授權、導入與支援，價格需報價；數位簽章另存在每張證書的第三方簽署／驗證費。 | 海事主管機關資料分散、難以持續提供線上驗證、STCW／IMO 合規負擔，以及缺乏安全的外部查詢與稽核軌跡。參考：[OHQ Cloud SaaS](https://www.oceanshq.com/products)、[證書外部驗證](https://www.oceanshq.com/products/stcw-convention)、[每張證書簽署成本](https://www.oceanshq.com/articles/digital-signatures-and-electronic-certificates/) |
| 10 | **天星管理顧問 Genius Star／臺灣** | 執行船舶 IHM 採樣、實驗室化驗、IHM 報告及送船級社／船旗國審查；在維護網站保存報告與證書，再依設備增減及 MD、SDoC 更新文件。這是專業文件維護，不是一般 B/L AI 比對。 | IHM 顧問、製作、送審及持續維護的 managed service；官網沒有公開價格，因此只能確認其銷售專業服務，無法確認是否逐船或逐年計價。 | 供應商材料聲明難以蒐集、設備更新後文件沒有同步、驗船送審負擔，以及 IHM 證據鏈與持續合規。參考：[官方 IHM 流程與實績](https://www.geniusstar.com.tw/zh_TW/web/ihm_service) |

## 獲利模式統整

| 獲利模式 | 代表業者 | 收入邏輯 |
|---|---|---|
| 按文件／inspection 計費 | Bol.ai、TradDocs | 文件量越大，收入越高；通常搭配最低月費、方案上限或免費額度。 |
| 按物流工作／交易計費 | CargoWise／Shipamax | 收費與 shipment、報關或其他物流工作量連動，不因 AI 減少使用者席次而降低收入。 |
| 年度企業 SaaS／API | Windward | 按資料覆蓋、功能深度、使用者、API 整合、服務及合約範圍報價。 |
| SaaS＋人工 managed service | Marcura、Expedock | 軟體處理標準案件，人員處理例外、品質保證、爭議、合規或 BPO。 |
| 軟體授權＋導入／顧問 | NewSoft、Oceans HQ | API、單機／雲端系統、客製欄位、後端整合、維護與顧問共同構成收入。 |
| 驗船／發證服務＋公開驗證 | DNV | 主要由檢驗、認證、審查及發證收費；線上查驗提升已核發證書的可信度。 |
| 逐案專業文件服務 | Genius Star | 執行資料蒐集、製作、送審及後續維護；收入更接近顧問與外包服務。 |

## 共同解決的使用者痛點

### 1. 人工輸入及比對量大

同一個船名、港口、櫃號、重量、數量與日期，要在 B/L、Invoice、Packing List、COO 及其他證書中重複核對與登打。文件一多，人工處理時間及遺漏機率同步增加。

### 2. 文件格式不統一

不同航商、代理商、船旗國及供應商使用不同版型、PDF、掃描圖片、email 或 Excel。傳統 template-based OCR 需要頻繁維護，難以涵蓋所有文件來源。

### 3. 小錯誤可能造成高額損失

欄位錯誤可能造成延遲付款、重新報關、貨物無法放行、交易融資延誤、制裁風險或主管機關罰款。港口支出帳單的費率、重複發票或漏用折扣，也會直接造成成本外漏。

### 4. 文件看起來真實，不代表內容真實

數位簽章及官方查驗可確認「誰簽發」及「是否仍有效」，但無法單獨證明文件描述的航程或原產地實際發生。Windward 類產品進一步把文件內容與 AIS、靠港紀錄、所有權及制裁資料比對，處理的是不同層次的風險。

### 5. 證書版本、簽註與效期難管理

船上、岸端、船級社及代理人可能持有不同版本；部分證書還有年度、中期或展期簽註。只保存 PDF 而沒有來源驗證、到期警示及稽核軌跡，仍可能在港口國檢查時出現問題。

### 6. 現有系統整合困難

若比對結果不能直接寫入 CargoWise、ERP、TMS、VMS 或政府平台，使用者仍必須重新輸入或複製資料，使自動化只取代一小段流程。

## 臺灣市場判斷

### 已存在的供應者

- **最接近跨文件 AI 比對：**力新國際已公開提供 Invoice、B/L、Packing List 的資料擷取及交叉比較，但它是通用企業 AI-OCR／系統整合商，不是純海事 SaaS。
- **船舶專業文件維護：**天星管理顧問聚焦 IHM 文件製作、送審及持續維護，海事專業深度較高，但不是廣泛的提單或船舶證書比對平台。
- **驗船及證書核發：**[財團法人驗船中心 CR](https://www.crclass.org/)及[法國驗船協會臺灣](https://www.bureauveritas.com.tw/marine)提供驗船、入級、認證及證書服務，屬船級與合規機構，不是跨文件 AI 比對 SaaS。

### 政府公共查驗已涵蓋部分需求

船員手冊、適任證書、僱外許可及海事勞工證書等文件已有[交通部航港局線上查驗服務](https://www.gov.tw/News_Content_2_375791)。官方同時說明，查驗功能主要確認航港局是否曾核發該文件；若仍有疑問，還要核對其他身分證明。因此，「政府證書是否核發」較接近公共基礎設施，不一定是最適合民間 SaaS 切入的市場。

### 公開政策證實文件比對需求存在

交通部航港局 115 年度施政內容已明確提出運用 AI 輔助船舶文件比對與審查；「我國海事人員智慧數位升級計畫」亦提到既有人工審查需要比對航商上傳的掃描文件，AI 可提高文件審查效率。這證實臺灣確實存在人工審查負擔，但也代表部分需求可能由政府自行建置。

參考：[航港局施政計畫](https://www.motcmpb.gov.tw/Article?NodeId=9&SiteId=1)、[我國海事人員智慧數位升級計畫](https://www.motcmpb.gov.tw/ServerFile/Get/455f237e-e180-4820-b6de-6f1fcc477fd9?DLCount=1)

## 法規與長期市場驅動力

IMO 將電子證書的「驗證」定義為可靠、安全且持續可用的程序，用唯一追蹤碼及證書內嵌資料確認真實性與有效性。電子證書還應符合下列要求：

- 符合相關國際公約的格式與內容；
- 防止未經授權的修改；
- 具備用於驗證的唯一追蹤碼；
- 具備可見、可列印的簽發來源標誌；
- 線上驗證網站應具備存取控制、防詐、抗網路攻擊及營運韌性。

此外，自 2024 年 1 月起，IMO 會員國必須使用 Maritime Single Window 電子交換船舶靠港所需資訊。這些規範持續推動文件標準化、電子驗證、資料交換及資訊安全需求。

參考：[IMO 電子證書使用指南 FAL.5/Circ.39/Rev.2](https://wwwcdn.imo.org/localresources/en/OurWork/Facilitation/Documents/FAL.5-Circ.39-Rev.2%20-%20Guidelines%20For%20The%20Use%20Of%20Electronic%20Certificates%20%28Secretariat%29.pdf)、[IMO Maritime Single Window](https://www.imo.org/en/ourwork/facilitation/pages/maritimesinglewindow-default.aspx)、[IMO Certificates and E-certificates](https://www.imo.org/en/ourwork/facilitation/pages/declarationscertificates-default.aspx)

## 市場缺口與產品定位觀察

依本次公開資料，臺灣市場最明顯的缺口不是單純 OCR，而是把以下能力整合成一個可以直接進入既有工作流程的產品：

1. B/L、Invoice、Packing List、COO、證書及契約的多文件欄位比對；
2. 中文與英文公司名稱、地址、日期、重量單位及港口名稱的正規化；
3. 船名、IMO Number、AIS 航跡、實際靠港、所有權及制裁資料驗證；
4. 船級社、船旗國及政府證書的官方查驗連結或 UTN／QR 驗證；
5. CargoWise、ERP、TMS、VMS 或 MTNet 相關流程的 API 整合；
6. 低信心或高風險差異的人工作業佇列、覆核紀錄及完整稽核軌跡。

如果產品只有 OCR，會直接面對 NewSoft、Shipamax、Expedock、Bol.ai 及通用 Document AI 的競爭；若加入船舶行為、所有權、制裁及官方證書來源驗證，則更接近 Windward 與船級社所占據的高價值合規市場。

## 證據限制

- 功能、效率、準確率、節省金額及客戶成果若取自供應商官網，屬供應商陳述，不應視為獨立第三方驗證。
- 收費模式優先採用官方定價頁、服務合約、公司年度報告或正式新聞稿；沒有公開價格者均標示為「洽詢」或「無法確認」，沒有自行推估價格。
- 搜尋結果會因日期、地區、語言及搜尋引擎索引變動。本文應在重大採購、投資或產品決策前重新查核。

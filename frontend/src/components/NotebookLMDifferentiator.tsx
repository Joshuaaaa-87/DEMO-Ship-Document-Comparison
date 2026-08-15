import React from 'react';
import { CheckCircle2, XCircle, Scale } from 'lucide-react';

export const NotebookLMDifferentiator: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl mb-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
          <Scale className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-100">
            為何選擇本 AI 船舶差異 Agent，而非 NotebookLM？
          </h2>
          <p className="text-sm text-slate-400">
            NotebookLM 為通用型 RAG 筆記工具，不具備船舶工程高安全嚴謹度、工安數值自動標紅與強制審查簽核軌跡。
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800/80 border border-teal-500/40 rounded-xl p-5 relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-teal-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider">
            本專案 (Dedicated Ship Doc Agent)
          </div>

          <h3 className="text-lg font-bold text-teal-400 mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-teal-400" />
            專為船舶與工安設計之嚴謹對照
          </h3>

          <ul className="space-y-3 text-sm text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-white">100% 精準頁碼與原始段落對照 (S1000D)</strong>：
                每筆變更皆可直接跳轉雙欄 PDF 原始印刷頁與 Line-by-line 對照，絕無 LLM 幻覺與語義遺漏。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-white">工安數值門檻自動標紅警示 (High Risk)</strong>：
                針對壓力 (bar/MPa)、溫度 (°C)、保養頻率與禁止語句，具備規則+AI 雙重警示機制。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-white">強制人工審查關卡與 Audit Trail 簽核</strong>：
                具備 Approve/Disapprove 點擊勾選與備註，未覆核之 High 項目禁止直接產出最終報告。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-400 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-white">3~5 版多版本橫向時間軸演進矩陣</strong>：
                一頁縱覽 v1.0 至 v2.0 同一設備與程序條文之演變歷史。
              </div>
            </li>
          </ul>
        </div>

        <div className="bg-slate-800/40 border border-slate-700/60 rounded-xl p-5 relative opacity-85">
          <div className="absolute top-0 right-0 bg-slate-700 text-slate-300 text-[10px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider">
            NotebookLM / 通用 RAG
          </div>

          <h3 className="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
            <XCircle className="w-5 h-5 text-slate-400" />
            通用筆記與對話侷限
          </h3>

          <ul className="space-y-3 text-sm text-slate-400">
            <li className="flex items-start gap-2">
              <span className="text-slate-500 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-slate-200">僅提供模糊大意摘要</strong>：
                無行級（Line-by-line）極度精準之新增/刪除/修改對齊，缺乏雙欄原始 PDF 閱讀器。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-500 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-slate-200">無工安數值變更等級判別</strong>：
                無法將 85°C 降為 80°C 判別為 High Risk 警示，容易讓工程師漏看重大工安更新。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-500 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-slate-200">無工程簽核與責任歸屬</strong>：
                無法在畫面上逐項勾選「已覆核」並寫入帶有時間戳記之法遵簽核報告。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-500 font-bold mt-0.5">•</span>
              <div>
                <strong className="text-slate-200">僅限對話問答，無正式 DOCX/PDF 匯出</strong>：
                無法依據企業標準版型匯出包含簽核欄位之維修審定報告。
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

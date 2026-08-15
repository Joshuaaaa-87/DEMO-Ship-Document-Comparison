import React from 'react';
import { CheckCircle2, XCircle, Scale } from 'lucide-react';

export const NotebookLMDifferentiator: React.FC = () => {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs space-y-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-amber-50 text-amber-700 rounded border border-amber-200">
          <Scale className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-800">
            為何選擇本 AI 船舶差異 Agent，而非 NotebookLM？
          </h2>
          <p className="text-xs text-slate-500">
            NotebookLM 為通用型 RAG 筆記工具，不具備船舶工程高安全嚴謹度、工安數值自動標紅與強制審查簽核軌跡。
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Dedicated Agent */}
        <div className="bg-teal-50/50 border border-teal-200 rounded-lg p-4 space-y-3">
          <h3 className="text-sm font-bold text-teal-800 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-teal-600" />
            專為船舶與高風險工程設計之嚴謹對照
          </h3>

          <ul className="space-y-2 text-xs text-slate-700">
            <li className="flex items-start gap-2">
              <span className="text-teal-700 font-bold">•</span>
              <div>
                <strong className="text-teal-900">100% 精準頁碼與原始段落對照 (S1000D)</strong>：
                每筆變更皆可直接跳轉雙欄 PDF 原始印刷頁與 Line-by-line 對照，絕無 LLM 幻覺與語義遺漏。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-700 font-bold">•</span>
              <div>
                <strong className="text-teal-900">工安數值門檻自動標紅警示 (High Risk)</strong>：
                針對壓力 (bar/MPa)、溫度 (°C)、保養頻率與禁止語句，具備規則+AI 雙重警示機制。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-teal-700 font-bold">•</span>
              <div>
                <strong className="text-teal-900">強制人工審查關卡與 Audit Trail 簽核</strong>：
                具備 Approve/Disapprove 點擊勾選與備註，未覆核之 High 項目禁止直接產出最終報告。
              </div>
            </li>
          </ul>
        </div>

        {/* NotebookLM / Generic RAG */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <h3 className="text-sm font-bold text-slate-700 flex items-center gap-2">
            <XCircle className="w-4 h-4 text-slate-400" />
            通用筆記與對話侷限
          </h3>

          <ul className="space-y-2 text-xs text-slate-600">
            <li className="flex items-start gap-2">
              <span className="text-slate-400 font-bold">•</span>
              <div>
                <strong className="text-slate-800">僅提供模糊大意摘要</strong>：
                無行級（Line-by-line）極度精準之新增/刪除/修改對齊，缺乏雙欄原始 PDF 閱讀器。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-400 font-bold">•</span>
              <div>
                <strong className="text-slate-800">無工安數值變更等級判別</strong>：
                無法將 85°C 降為 80°C 判別為 High Risk 警示，容易讓工程師漏看重大工安更新。
              </div>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-slate-400 font-bold">•</span>
              <div>
                <strong className="text-slate-800">無工程簽核與責任歸屬</strong>：
                無法在畫面上逐項勾選「已覆核」並寫入帶有時間戳記之法遵簽核報告。
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

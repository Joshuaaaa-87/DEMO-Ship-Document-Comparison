import React, { useState } from 'react';
import { Wrench, ChevronDown, ChevronUp, AlertOctagon } from 'lucide-react';
import type { Difference } from '../types';

interface EngineerDashboardProps {
  differences: Difference[];
  onUpdateDifference: (id: string, review_status: Difference['review_status'], reviewer_note: string) => void;
  scannedOld: number[];
  scannedNew: number[];
}

export const EngineerDashboard: React.FC<EngineerDashboardProps> = ({
  differences,
  onUpdateDifference,
  scannedOld,
  scannedNew,
}) => {
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-5">
      
      {/* Subheader Notice (V1 Light Style) */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-teal-50 text-teal-700 rounded border border-teal-200">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">
              維修工程師 — 可追溯差異對照清單
            </h2>
            <p className="text-xs text-slate-500">
              核對 PDF 頁碼與原文段落，進行人工覆核與簽核筆記填寫
            </p>
          </div>
        </div>
      </div>

      {/* Scanned PDF Alert Banner (V1 Style: Amber warning) */}
      {(scannedOld.length > 0 || scannedNew.length > 0) && (
        <div className="bg-amber-50 border border-amber-300 text-amber-900 rounded-lg p-3.5 flex items-center gap-3 text-xs shadow-xs">
          <AlertOctagon className="w-5 h-5 text-amber-600 flex-shrink-0" />
          <div>
            <strong className="text-amber-800">⚠️ 掃描檔/圖檔警示：</strong>
            檢測到部分頁面無文字層 (舊版 p.{scannedOld.join(',') || '無'} / 新版 p.{scannedNew.join(',') || '無'})，建議進行 OCR 或人工雙重校對。
          </div>
        </div>
      )}

      {/* Differences List (Matching V1 Streamlit Card/Expander Design) */}
      <div className="space-y-3">
        {differences.map((item) => {
          const isExpanded = expandedItems[item.id] ?? (item.risk === 'High');
          const marker = item.risk === 'High' ? '🔴' : item.risk === 'Medium' ? '🟠' : '🟢';

          return (
            <div
              key={item.id}
              className={`bg-white border rounded-lg p-4 transition-all shadow-xs ${
                item.risk === 'High'
                  ? 'border-rose-300 border-l-4 border-l-rose-600'
                  : 'border-slate-200'
              }`}
            >
              {/* Expander Header Row (Exact V1 Streamlit Title Format) */}
              <div
                onClick={() => toggleExpand(item.id)}
                className="flex items-center justify-between cursor-pointer select-none"
              >
                <div className="flex items-center gap-2 flex-wrap text-xs">
                  <span className="text-sm">{marker}</span>
                  <span className="font-mono font-bold text-slate-700">{item.id}</span>
                  <span className="text-slate-300">|</span>
                  <span className="font-semibold text-teal-700">{item.change_type}</span>
                  <span className="text-slate-300">|</span>
                  <span className="text-slate-700 font-bold">
                    風險：
                    <span className={item.risk === 'High' ? 'text-rose-700' : item.risk === 'Medium' ? 'text-amber-700' : 'text-emerald-700'}>
                      {item.risk}
                    </span>
                  </span>
                  <span className="text-slate-300">|</span>
                  <span className="text-slate-800 font-bold">受影響設備：{item.affected}</span>
                </div>

                <div className="p-1 text-slate-400 hover:text-slate-600">
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
              </div>

              {/* Expander Body (Matching V1 Dual-Column Excerpts & Form) */}
              {isExpanded && (
                <div className="mt-4 pt-3 border-t border-slate-200 space-y-4">
                  
                  {/* Dual Column Excerpts */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    {/* Old Source */}
                    <div className="space-y-1">
                      <div className="text-slate-500 font-medium flex justify-between">
                        <span>舊版來源：</span>
                        <span className="font-mono text-slate-700 font-bold">PDF p.{item.old?.page || '-'}</span>
                      </div>
                      <div className="bg-slate-100 p-3 rounded border border-slate-200 font-mono text-slate-800 leading-relaxed whitespace-pre-wrap text-[11px]">
                        {item.old?.text || '（新增段落）'}
                      </div>
                    </div>

                    {/* New Source (V1 Mint Excerpt Style) */}
                    <div className="space-y-1">
                      <div className="text-teal-700 font-medium flex justify-between">
                        <span>新版來源：</span>
                        <span className="font-mono text-teal-800 font-bold">PDF p.{item.new?.page || '-'}</span>
                      </div>
                      <div className="bg-teal-50 p-3 rounded border border-teal-200 text-teal-900 font-mono leading-relaxed whitespace-pre-wrap text-[11px]">
                        {item.new?.text || '（刪除段落）'}
                      </div>
                    </div>
                  </div>

                  {/* Interpretations */}
                  <div className="text-xs space-y-1 pt-1 border-t border-slate-100">
                    <div>
                      <strong className="text-slate-700">變更解讀：</strong>
                      <span className="text-slate-700 leading-relaxed">{item.explanation}</span>
                    </div>
                    <div>
                      <strong className="text-slate-700">受影響設備/流程：</strong>
                      <span className="text-slate-800">{item.affected}</span>
                      <span className="text-slate-300 mx-2">｜</span>
                      <strong className="text-slate-700">信心度：</strong>
                      <span className="text-slate-800">{item.confidence}</span>
                    </div>
                    <div>
                      <strong className="text-amber-800">建議處置：</strong>
                      <span className="text-amber-900 font-medium">{item.recommended_action}</span>
                    </div>
                  </div>

                  {/* Review Inputs */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-center pt-2 bg-slate-50 p-3 rounded border border-slate-200">
                    <div>
                      <label className="block text-[11px] text-slate-500 mb-1 font-medium">
                        人工覆核狀態
                      </label>
                      <select
                        value={item.review_status}
                        onChange={(e) =>
                          onUpdateDifference(
                            item.id,
                            e.target.value as Difference['review_status'],
                            item.reviewer_note
                          )
                        }
                        className="w-full bg-white text-slate-800 border border-slate-300 rounded px-2.5 py-1.5 text-xs font-semibold shadow-xs"
                      >
                        <option value="未覆核">未覆核</option>
                        <option value="已確認">已確認</option>
                        <option value="需追蹤">需追蹤</option>
                        <option value="不採納">不採納</option>
                      </select>
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-[11px] text-slate-500 mb-1 font-medium">
                        覆核理由 / 審核筆記
                      </label>
                      <input
                        type="text"
                        value={item.reviewer_note}
                        placeholder="輸入工程確認筆記..."
                        onChange={(e) =>
                          onUpdateDifference(item.id, item.review_status, e.target.value)
                        }
                        className="w-full bg-white text-slate-800 border border-slate-300 rounded px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500 shadow-xs"
                      />
                    </div>
                  </div>

                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
};

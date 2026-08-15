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

  const reviewedCount = differences.filter((d) => d.review_status !== '未覆核').length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      
      {/* Subheader / Status Summary */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-teal-500/10 text-teal-400 rounded-lg">
            <Wrench className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100">
              維修工程師 — SOP 條文變更審查清單
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              逐筆核對 PDF 頁碼原文、工安數值差異，並填寫工程覆核備註
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="text-slate-400">
            覆核進度：<strong className="text-teal-400 font-bold">{reviewedCount} / {differences.length} 筆</strong>
          </div>
        </div>
      </div>

      {/* Scanned OCR Notice if applicable */}
      {(scannedOld.length > 0 || scannedNew.length > 0) && (
        <div className="bg-amber-950/40 border border-amber-500/30 text-amber-200 rounded-xl p-4 flex items-center gap-3 text-xs">
          <AlertOctagon className="w-5 h-5 text-amber-400 flex-shrink-0" />
          <div>
            <strong>圖檔頁面警示：</strong>
            舊版 p.{scannedOld.join(',') || '無'} / 新版 p.{scannedNew.join(',') || '無'} 缺乏文字層，建議人工對照原始掃描圖檔。
          </div>
        </div>
      )}

      {/* Difference Cards List */}
      <div className="space-y-4">
        {differences.map((item) => {
          const isExpanded = expandedItems[item.id] ?? (item.risk === 'High');

          return (
            <div
              key={item.id}
              className={`bg-slate-900 border rounded-xl p-5 transition-all shadow-sm ${
                item.risk === 'High'
                  ? 'border-rose-900/60 hover:border-rose-700/80'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              {/* Card Top Row */}
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                      {item.id}
                    </span>

                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded ${
                        item.risk === 'High'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : item.risk === 'Medium'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}
                    >
                      {item.risk} Risk
                    </span>

                    <span className="text-xs text-slate-300 font-semibold bg-slate-800/80 px-2 py-0.5 rounded">
                      {item.change_type}
                    </span>

                    <h3 className="text-sm font-bold text-slate-100">
                      {item.affected}
                    </h3>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed pt-1">
                    {item.explanation}
                  </p>
                </div>

                <button
                  onClick={() => toggleExpand(item.id)}
                  className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-all flex-shrink-0"
                >
                  {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>
              </div>

              {/* Side-by-side Text Excerpts */}
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-slate-800 space-y-4">
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Old Excerpt */}
                    <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80 space-y-1">
                      <div className="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
                        <span>舊版原文段落</span>
                        <span className="text-slate-500 font-mono">PDF p.{item.old?.page || '-'}</span>
                      </div>
                      <p className="text-xs text-slate-300 font-mono leading-relaxed bg-slate-900/60 p-2 rounded border border-slate-800">
                        {item.old?.text || '（無對應舊版段落）'}
                      </p>
                    </div>

                    {/* New Excerpt */}
                    <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80 space-y-1">
                      <div className="text-[11px] font-semibold text-teal-400 flex items-center justify-between">
                        <span>新版對照段落 (變更處)</span>
                        <span className="text-teal-500 font-mono">PDF p.{item.new?.page || '-'}</span>
                      </div>
                      <p className="text-xs text-teal-200 font-mono leading-relaxed bg-teal-950/30 p-2 rounded border border-teal-900/40">
                        {item.new?.text || '（無對應新版段落）'}
                      </p>
                    </div>
                  </div>

                  {/* Recommendation & Review Form */}
                  <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/60 space-y-3">
                    <div className="text-xs text-amber-300 font-semibold flex items-center gap-1.5">
                      <span>💡 建議工程處置：</span>
                      <span className="text-slate-200 font-normal">{item.recommended_action}</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-center pt-2">
                      <div>
                        <label className="block text-[11px] text-slate-400 mb-1 font-medium">
                          審查狀態
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
                          className="w-full bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-medium"
                        >
                          <option value="未覆核">未覆核</option>
                          <option value="已確認">已確認 (Approve)</option>
                          <option value="需追蹤">需追蹤 (Follow-up)</option>
                          <option value="不採納">不採納 (Reject)</option>
                        </select>
                      </div>

                      <div className="sm:col-span-2">
                        <label className="block text-[11px] text-slate-400 mb-1 font-medium">
                          覆核筆記與備註
                        </label>
                        <input
                          type="text"
                          value={item.reviewer_note}
                          placeholder="輸入覆核筆記（如：已對照驗船最新規範...）"
                          onChange={(e) =>
                            onUpdateDifference(item.id, item.review_status, e.target.value)
                          }
                          className="w-full bg-slate-900 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
                        />
                      </div>
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

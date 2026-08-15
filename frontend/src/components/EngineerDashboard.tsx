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
  const [selectedId, setSelectedId] = useState<string>(differences[0]?.id || 'D01');
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string) => {
    setExpandedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-teal-900/40 via-slate-900 to-slate-900 border border-teal-500/30 rounded-2xl p-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-teal-600/20 text-teal-400 rounded-xl border border-teal-500/30">
            <Wrench className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              🔧 第一線維修工程師對照視圖 (Field Engineer Detailed SOP View)
            </h2>
            <p className="text-xs text-slate-400">
              提供 100% 精準頁碼原文對照、設備料號比對、建議處置與即時簽核紀錄
            </p>
          </div>
        </div>
      </div>

      {(scannedOld.length > 0 || scannedNew.length > 0) && (
        <div className="bg-amber-950/80 border border-amber-500 text-amber-200 rounded-2xl p-4 flex items-center gap-3">
          <AlertOctagon className="w-6 h-6 text-amber-400 flex-shrink-0" />
          <div className="text-xs">
            <strong className="text-sm font-bold text-amber-300">掃描檔/圖檔警示 (OCR Notice)：</strong>
            檢測到部分頁面無文字層 (舊版 p.{scannedOld.join(',') || '無'} / 新版 p.{scannedNew.join(',') || '無'})，建議進行人工校對，防範漏看重大變更。
          </div>
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center justify-between">
          <span>可追溯差異細節清單 (Total: {differences.length} 筆)</span>
          <span className="text-xs text-slate-400 font-normal">點擊項目可展開詳細對照與填寫簽核筆記</span>
        </h3>

        <div className="space-y-3">
          {differences.map((item) => {
            const isExpanded = expandedItems[item.id] ?? (item.risk === 'High');
            const isSelected = item.id === selectedId;

            return (
              <div
                key={item.id}
                onClick={() => setSelectedId(item.id)}
                className={`border rounded-xl p-4 transition-all cursor-pointer ${
                  isSelected
                    ? 'border-teal-500 bg-slate-800/80 shadow-lg shadow-teal-950/40'
                    : 'border-slate-800 bg-slate-800/30 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                        item.risk === 'High'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : item.risk === 'Medium'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {item.id} • {item.risk} Risk
                    </span>
                    <span className="text-xs font-bold bg-slate-700/60 text-slate-200 px-2 py-0.5 rounded">
                      {item.change_type}
                    </span>
                    <h4 className="text-sm font-bold text-slate-200">{item.affected}</h4>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleExpand(item.id);
                    }}
                    className="p-1 text-slate-400 hover:text-slate-200"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>

                <p className="text-xs text-slate-300 mt-2 font-medium">{item.explanation}</p>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-slate-700/60 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                        <div className="text-[11px] text-slate-400 font-semibold mb-1">
                          舊版原文 (PDF p.{item.old?.page || '-'})
                        </div>
                        <code className="text-slate-300 font-mono text-[11px] block whitespace-pre-wrap">
                          {item.old?.text || '（無對應舊版段落）'}
                        </code>
                      </div>

                      <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                        <div className="text-[11px] text-slate-400 font-semibold mb-1">
                          新版原文 (PDF p.{item.new?.page || '-'})
                        </div>
                        <code className="text-slate-300 font-mono text-[11px] block whitespace-pre-wrap">
                          {item.new?.text || '（無對應新版段落）'}
                        </code>
                      </div>
                    </div>

                    <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800/80 space-y-3">
                      <div className="text-xs text-amber-400 font-semibold">
                        💡 建議工程處置：{item.recommended_action}
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-center">
                        <div>
                          <label className="block text-[11px] text-slate-400 mb-1 font-medium">
                            覆核簽核狀態
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
                            className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs font-semibold"
                          >
                            <option value="未覆核">未覆核</option>
                            <option value="已確認">已確認 (Approve)</option>
                            <option value="需追蹤">需追蹤 (Follow-up)</option>
                            <option value="不採納">不採納 (Reject)</option>
                          </select>
                        </div>

                        <div className="sm:col-span-2">
                          <label className="block text-[11px] text-slate-400 mb-1 font-medium">
                            審核筆記 / 簽核理由
                          </label>
                          <input
                            type="text"
                            value={item.reviewer_note}
                            placeholder="輸入工程確認筆記（如：已對照 2026 最新檢驗標準...）"
                            onChange={(e) =>
                              onUpdateDifference(item.id, item.review_status, e.target.value)
                            }
                            className="w-full bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
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
    </div>
  );
};

import React from 'react';
import { ShieldAlert, AlertTriangle, Activity, Clock, FileText } from 'lucide-react';
import type { Difference } from '../types';

interface ManagerDashboardProps {
  differences: Difference[];
  onExportDocx: () => void;
}

export const ManagerDashboard: React.FC<ManagerDashboardProps> = ({
  differences,
  onExportDocx,
}) => {
  const highRiskCount = differences.filter((d) => d.risk === 'High').length;
  const reviewedCount = differences.filter((d) => d.review_status !== '未覆核').length;
  const unreviewedHighCount = differences.filter((d) => d.risk === 'High' && d.review_status === '未覆核').length;
  const reviewRate = differences.length > 0 ? Math.round((reviewedCount / differences.length) * 100) : 0;

  const highRiskItems = differences.filter((d) => d.risk === 'High');

  return (
    <div className="space-y-6">
      
      {/* Executive Header Bar (V1 Light Style) */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-rose-50 text-rose-700 rounded border border-rose-200">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">
              安品主管 — 工安風險與審查簽核控管
            </h2>
            <p className="text-xs text-slate-500">
              即時掌握重大工安變更、完成率與 Audit Trail 合規軌跡
            </p>
          </div>
        </div>

        <button
          onClick={onExportDocx}
          className="px-4 py-2 bg-teal-700 hover:bg-teal-600 text-white rounded font-bold text-xs transition-all flex items-center gap-2 shadow-xs"
        >
          <FileText className="w-4 h-4" />
          匯出 DOCX 簽核報告
        </button>
      </div>

      {/* Unreviewed High-Risk Alert Banner (V1 Warning Banner Style: #ffebe9 / #b43b37) */}
      {unreviewedHighCount > 0 && (
        <div className="bg-rose-50 border border-rose-300 text-rose-800 rounded-lg p-3.5 flex items-center gap-3 text-xs font-medium shadow-xs">
          <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          <div>
            <strong className="text-rose-700">⚠️ 工安合規警示：</strong>
            您目前仍有 <span className="underline font-bold text-rose-900">{unreviewedHighCount} 項 High 重大安全變更</span> 尚未進行人工覆核！導出報告將標註為修訂草稿。
          </div>
        </div>
      )}

      {/* 4 Metric Cards (Matching V1 Left-Border Accent Cards) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Total */}
        <div className="bg-white border border-slate-200 border-l-4 border-l-teal-600 rounded-lg p-4 shadow-xs">
          <div className="text-xs text-slate-500 mb-1">總差異筆數 / Total</div>
          <div className="text-2xl font-bold text-teal-700">{differences.length}</div>
        </div>

        {/* High Risk */}
        <div className="bg-white border border-slate-200 border-l-4 border-l-rose-600 rounded-lg p-4 shadow-xs">
          <div className="text-xs text-slate-500 mb-1">重大候選 / High Risk</div>
          <div className="text-2xl font-bold text-rose-700">{highRiskCount}</div>
        </div>

        {/* Reviewed */}
        <div className="bg-white border border-slate-200 border-l-4 border-l-emerald-600 rounded-lg p-4 shadow-xs">
          <div className="text-xs text-slate-500 mb-1">已完成覆核 / Reviewed</div>
          <div className="text-2xl font-bold text-emerald-700">{reviewedCount} ({reviewRate}%)</div>
        </div>

        {/* Unreviewed High */}
        <div className="bg-white border border-slate-200 border-l-4 border-l-amber-600 rounded-lg p-4 shadow-xs">
          <div className="text-xs text-slate-500 mb-1">待簽核重大項目</div>
          <div className="text-2xl font-bold text-amber-700">{unreviewedHighCount}</div>
        </div>
      </div>

      {/* Executive Action Items */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-3 shadow-xs">
        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <Activity className="w-4 h-4 text-teal-700" />
          主管優先行動清單 (Executive Action Items)
        </h3>

        {highRiskItems.length === 0 ? (
          <p className="text-xs text-slate-500">尚無重大工安變更項目。</p>
        ) : (
          <div className="space-y-2.5">
            {highRiskItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-50 border border-slate-200 rounded p-3 flex items-center justify-between gap-4 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="bg-rose-100 text-rose-700 font-mono font-bold px-2 py-0.5 rounded text-[10px] border border-rose-300">
                      {item.id} High Risk
                    </span>
                    <strong className="text-slate-800">{item.affected}</strong>
                  </div>
                  <p className="text-slate-600">{item.explanation}</p>
                </div>

                <div className="text-right flex-shrink-0 space-y-1">
                  <div className="text-amber-800 font-semibold">
                    建議：{item.recommended_action}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    狀態：
                    <span className={item.review_status !== '未覆核' ? 'text-teal-700 font-bold' : 'text-rose-700 font-bold'}>
                      {item.review_status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compliance Log / Audit Trail (V1 Table Style: #e8f7f5 Header) */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 space-y-3 shadow-xs">
        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-500" />
          審查紀錄與 Audit Trail 軌跡 (Compliance Log)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-700">
            <thead className="bg-teal-50 text-teal-800 uppercase text-[10px] font-bold border-b border-teal-200">
              <tr>
                <th className="px-3 py-2.5">ID</th>
                <th className="px-3 py-2.5">風險</th>
                <th className="px-3 py-2.5">受影響設備</th>
                <th className="px-3 py-2.5">覆核狀態</th>
                <th className="px-3 py-2.5">審核備註</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {differences.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="px-3 py-2 font-mono font-bold text-slate-700">{item.id}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        item.risk === 'High'
                          ? 'bg-rose-100 text-rose-700 border border-rose-200'
                          : item.risk === 'Medium'
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                      }`}
                    >
                      {item.risk}
                    </span>
                  </td>
                  <td className="px-3 py-2 font-medium text-slate-800">{item.affected}</td>
                  <td className="px-3 py-2 font-semibold">{item.review_status}</td>
                  <td className="px-3 py-2 text-slate-600">{item.reviewer_note || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

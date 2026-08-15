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
    <div className="space-y-6 max-w-5xl mx-auto">
      
      {/* Executive Subheader */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100">
              安品與技術主管 — 工安變更與合規簽核視圖
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              掌握重大工安變更、覆核進度與 Audit Trail 不可竄改之合規軌跡
            </p>
          </div>
        </div>

        <button
          onClick={onExportDocx}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition-all shadow-sm flex items-center gap-2"
        >
          <FileText className="w-4 h-4" />
          匯出 DOCX 簽核報告
        </button>
      </div>

      {/* Unreviewed High-Risk Warning Alert */}
      {unreviewedHighCount > 0 && (
        <div className="bg-rose-950/40 border border-rose-600/40 text-rose-200 rounded-xl p-4 flex items-center gap-3 text-xs">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          <div>
            <strong>工安合規警示：</strong>
            仍有 <span className="underline font-bold text-white">{unreviewedHighCount} 項 High 重大安全變更</span> 尚未完成工程覆核，匯出報告將標註為修訂草稿。
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <div className="text-xs text-slate-400 font-medium">總變更筆數</div>
          <div className="text-2xl font-bold text-slate-100">{differences.length}</div>
        </div>
        <div className="bg-slate-900 border border-rose-900/40 rounded-xl p-4 space-y-1">
          <div className="text-xs text-rose-400 font-medium">High 重大工安變更</div>
          <div className="text-2xl font-bold text-rose-400">{highRiskCount}</div>
        </div>
        <div className="bg-slate-900 border border-teal-900/40 rounded-xl p-4 space-y-1">
          <div className="text-xs text-teal-400 font-medium">工程覆核達成率</div>
          <div className="text-2xl font-bold text-teal-400">{reviewRate}%</div>
        </div>
        <div className="bg-slate-900 border border-amber-900/40 rounded-xl p-4 space-y-1">
          <div className="text-xs text-amber-400 font-medium">待簽核重大項目</div>
          <div className="text-2xl font-bold text-amber-400">{unreviewedHighCount}</div>
        </div>
      </div>

      {/* Executive Action Items */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Activity className="w-4 h-4 text-teal-400" />
          主管優先處置清單 (Executive Action Items)
        </h3>

        {highRiskItems.length === 0 ? (
          <p className="text-xs text-slate-500">尚無重大工安變更項目。</p>
        ) : (
          <div className="space-y-3">
            {highRiskItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-950/60 border border-slate-800 rounded-lg p-3.5 flex items-center justify-between gap-4 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="bg-rose-500/20 text-rose-300 font-mono font-bold px-2 py-0.5 rounded text-[10px]">
                      {item.id} High
                    </span>
                    <strong className="text-slate-200">{item.affected}</strong>
                  </div>
                  <p className="text-slate-400">{item.explanation}</p>
                </div>

                <div className="text-right flex-shrink-0 space-y-1">
                  <div className="text-amber-300 font-medium">
                    建議：{item.recommended_action}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    狀態：
                    <span className={item.review_status !== '未覆核' ? 'text-teal-400 font-bold' : 'text-rose-400 font-bold'}>
                      {item.review_status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compliance Log / Audit Trail */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          審查紀錄與 Audit Trail 軌跡 (Compliance Log)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] font-semibold">
              <tr>
                <th className="px-3 py-2">ID</th>
                <th className="px-3 py-2">風險</th>
                <th className="px-3 py-2">受影響設備</th>
                <th className="px-3 py-2">覆核狀態</th>
                <th className="px-3 py-2">審核備註</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {differences.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/40">
                  <td className="px-3 py-2 font-mono font-bold text-slate-400">{item.id}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        item.risk === 'High'
                          ? 'bg-rose-500/20 text-rose-300'
                          : item.risk === 'Medium'
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-emerald-500/20 text-emerald-300'
                      }`}
                    >
                      {item.risk}
                    </span>
                  </td>
                  <td className="px-3 py-2 font-medium text-slate-200">{item.affected}</td>
                  <td className="px-3 py-2 font-semibold">{item.review_status}</td>
                  <td className="px-3 py-2 text-slate-400">{item.reviewer_note || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

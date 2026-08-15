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
      <div className="bg-gradient-to-r from-rose-900/40 via-slate-900 to-slate-900 border border-rose-500/30 rounded-2xl p-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-rose-600/20 text-rose-400 rounded-xl border border-rose-500/30">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              🛡️ 安品與技術主管審查視圖 (Safety & QA Executive View)
            </h2>
            <p className="text-xs text-slate-400">
              專注於高風險工安變更追蹤、覆核完成度與審查合規紀錄 (Audit Trail)
            </p>
          </div>
        </div>

        <button
          onClick={onExportDocx}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-rose-900/40 flex items-center gap-2"
        >
          <FileText className="w-4 h-4" />
          匯出正式 DOCX 簽核報告
        </button>
      </div>

      {unreviewedHighCount > 0 && (
        <div className="bg-rose-950/80 border border-rose-600 text-rose-200 rounded-2xl p-4 flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-rose-400 flex-shrink-0 animate-bounce" />
          <div className="text-xs">
            <strong className="text-sm font-bold text-rose-300">工安合規警示：</strong>
            仍有 <span className="underline font-bold text-white">{unreviewedHighCount} 項 High 重大安全變更</span> 尚未由工程人員進行人工審查！報告導出將標註為修訂草稿。
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="text-xs text-slate-400 font-medium">總變更筆數</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">{differences.length}</div>
        </div>
        <div className="bg-slate-900 border border-rose-900/50 rounded-2xl p-4 border-l-4 border-l-rose-500">
          <div className="text-xs text-rose-400 font-medium">High 重大安全變更</div>
          <div className="text-2xl font-bold text-rose-400 mt-1">{highRiskCount}</div>
        </div>
        <div className="bg-slate-900 border border-teal-900/50 rounded-2xl p-4 border-l-4 border-l-teal-500">
          <div className="text-xs text-teal-400 font-medium">人工覆核達成率</div>
          <div className="text-2xl font-bold text-teal-400 mt-1">{reviewRate}%</div>
        </div>
        <div className="bg-slate-900 border border-amber-900/50 rounded-2xl p-4 border-l-4 border-l-amber-500">
          <div className="text-xs text-amber-400 font-medium">待簽核重大項目</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{unreviewedHighCount}</div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-teal-400" />
          主管優先行動處置清單 (Executive Action Items)
        </h3>

        {highRiskItems.length === 0 ? (
          <p className="text-xs text-slate-500">尚無重大工安變更項目。</p>
        ) : (
          <div className="space-y-3">
            {highRiskItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-800/60 border border-slate-700/80 rounded-xl p-3.5 flex items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="bg-rose-500/20 text-rose-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-rose-500/30">
                      {item.id} High Risk
                    </span>
                    <span className="text-xs font-bold text-slate-200">{item.affected}</span>
                  </div>
                  <p className="text-xs text-slate-400">{item.explanation}</p>
                </div>

                <div className="text-right flex-shrink-0">
                  <div className="text-[11px] font-medium text-amber-400">
                    建議處置：{item.recommended_action}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    狀態：
                    <span
                      className={
                        item.review_status !== '未覆核'
                          ? 'text-teal-400 font-bold'
                          : 'text-rose-400 font-bold'
                      }
                    >
                      {item.review_status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          審查紀錄與 Audit Trail 軌跡 (Compliance Log)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-300">
            <thead className="bg-slate-800 text-slate-400 uppercase text-[10px] font-bold">
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
                  <td className="px-3 py-2 font-mono font-bold text-slate-300">{item.id}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                        item.risk === 'High'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : item.risk === 'Medium'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {item.risk}
                    </span>
                  </td>
                  <td className="px-3 py-2 font-medium text-slate-300">{item.affected}</td>
                  <td className="px-3 py-2 font-bold">{item.review_status}</td>
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

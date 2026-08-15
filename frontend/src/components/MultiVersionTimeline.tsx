import React from 'react';
import { History, GitCommit } from 'lucide-react';
import type { MultiVersionItem } from '../types';

export const MultiVersionTimeline: React.FC = () => {
  const timelineData: MultiVersionItem[] = [
    {
      section_id: 'S01',
      title: '主機冷卻液出口建議與限制溫度',
      v10: '建議維持在 85°C 以下',
      v11: '必須維持在 80°C 以下 (High Risk)',
      v12: '必須維持在 78°C 以下 (自動警示閥門)',
      v20: '必須維持在 75°C 以下 (聯鎖自動關斷保護)',
      risk: 'High',
      impact_equipment: '主機冷卻系統 / 溫度感測器',
    },
    {
      section_id: 'S02',
      title: '循環泵浦檢查與保養週期',
      v10: '每月檢查一次讀值',
      v11: '每週檢查一次讀值 (新增義務)',
      v12: '每週檢查讀值並每季更換濾心',
      v20: '每次啟動前自動自檢 + 每週人工覆核',
      risk: 'High',
      impact_equipment: '循環泵浦 / 濾心組件',
    },
    {
      section_id: 'S03',
      title: '密封件零件號碼 specification',
      v10: '零件號碼 CP-100 橡膠密封件',
      v11: '零件號碼 CP-120 耐熱密封件',
      v12: '零件號碼 CP-150 高壓金屬密封件',
      v20: '零件號碼 CP-200 複合雙重防洩密封件',
      risk: 'Medium',
      impact_equipment: '循環泵浦密封件',
    },
    {
      section_id: 'S04',
      title: '適用船型規範範圍 (Applicability)',
      v10: '巡防艦 A 型',
      v11: '巡防艦 A 型及 B 型',
      v12: '巡防艦 A, B, C 型',
      v20: '全系列巡防艦及支援艦型',
      risk: 'Medium',
      impact_equipment: '文件適用範圍',
    },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
            <History className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">
              📊 3~5 版多版本演進時間軸對照矩陣 (Multi-Version Timeline Matrix)
            </h2>
            <p className="text-xs text-slate-400">
              橫向縱覽同一程序條文於 v1.0 ➔ v1.1 ➔ v1.2 ➔ v2.0 跨版本之變化演進與風險脈絡
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-700">
          <GitCommit className="w-4 h-4 text-cyan-400" />
          <span>4 個版本比較中 (v1.0 ➔ v2.0)</span>
        </div>
      </div>

      <div className="space-y-4">
        {timelineData.map((item) => (
          <div
            key={item.section_id}
            className="bg-slate-800/50 border border-slate-700/80 rounded-xl p-5 hover:border-slate-600 transition-all space-y-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                    item.risk === 'High'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {item.risk} Risk
                </span>
                <h3 className="text-base font-bold text-slate-200">{item.title}</h3>
              </div>

              <div className="text-xs text-slate-400">
                影響設備：<span className="text-slate-200 font-semibold">{item.impact_equipment}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2">
              <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 relative">
                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                  v1.0 (基線)
                </div>
                <div className="text-xs text-slate-300 font-medium">{item.v10}</div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-lg border border-rose-900/50 relative border-l-4 border-l-rose-500">
                <div className="text-[10px] font-bold text-rose-400 uppercase tracking-wider mb-1">
                  v1.1 (改版)
                </div>
                <div className="text-xs text-rose-200 font-medium">{item.v11}</div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-lg border border-amber-900/50 relative border-l-4 border-l-amber-500">
                <div className="text-[10px] font-bold text-amber-400 uppercase tracking-wider mb-1">
                  v1.2 (權限)
                </div>
                <div className="text-xs text-amber-200 font-medium">{item.v12}</div>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-lg border border-teal-900/50 relative border-l-4 border-l-teal-500">
                <div className="text-[10px] font-bold text-teal-400 uppercase tracking-wider mb-1">
                  v2.0 (現行最新)
                </div>
                <div className="text-xs text-teal-200 font-medium">{item.v20}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

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
    <div className="bg-white border border-slate-200 rounded-lg p-5 space-y-5 shadow-xs">
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-teal-50 text-teal-700 rounded border border-teal-200">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">
              📊 3~5 版多版本演進時間軸對照矩陣 (Multi-Version Timeline Matrix)
            </h2>
            <p className="text-xs text-slate-500">
              橫向縱覽同一程序條文於 v1.0 ➔ v1.1 ➔ v1.2 ➔ v2.0 跨版本之變化演進與風險脈絡
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded border border-slate-200 font-medium">
          <GitCommit className="w-4 h-4 text-teal-700" />
          <span>4 個版本比較中 (v1.0 ➔ v2.0)</span>
        </div>
      </div>

      <div className="space-y-4">
        {timelineData.map((item) => (
          <div
            key={item.section_id}
            className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3 shadow-xs"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    item.risk === 'High'
                      ? 'bg-rose-100 text-rose-700 border border-rose-200'
                      : 'bg-amber-100 text-amber-800 border border-amber-200'
                  }`}
                >
                  {item.risk} Risk
                </span>
                <h3 className="text-sm font-bold text-slate-800">{item.title}</h3>
              </div>

              <div className="text-xs text-slate-500">
                影響設備：<span className="text-slate-800 font-semibold">{item.impact_equipment}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-1 text-xs">
              <div className="bg-white p-3 rounded border border-slate-200">
                <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">v1.0 (基線)</div>
                <div className="text-slate-700 font-medium">{item.v10}</div>
              </div>

              <div className="bg-rose-50/70 p-3 rounded border border-rose-200 border-l-4 border-l-rose-600">
                <div className="text-[10px] font-bold text-rose-700 uppercase mb-1">v1.1 (改版)</div>
                <div className="text-rose-900 font-medium">{item.v11}</div>
              </div>

              <div className="bg-amber-50/70 p-3 rounded border border-amber-200 border-l-4 border-l-amber-600">
                <div className="text-[10px] font-bold text-amber-800 uppercase mb-1">v1.2 (強化)</div>
                <div className="text-amber-950 font-medium">{item.v12}</div>
              </div>

              <div className="bg-teal-50/70 p-3 rounded border border-teal-200 border-l-4 border-l-teal-600">
                <div className="text-[10px] font-bold text-teal-800 uppercase mb-1">v2.0 (最新)</div>
                <div className="text-teal-950 font-medium">{item.v20}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

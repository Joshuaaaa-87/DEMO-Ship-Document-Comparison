import React, { useState } from 'react';
import { Download, FileText, Stamp } from 'lucide-react';
import type { Difference } from '../types';

interface ReportExporterProps {
  differences: Difference[];
  onExportDocx: () => void;
}

export const ReportExporter: React.FC<ReportExporterProps> = ({
  onExportDocx,
}) => {
  const [isExporting, setIsExporting] = useState(false);

  const handleDocxClick = async () => {
    setIsExporting(true);
    try {
      await onExportDocx();
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-rose-500/10 text-rose-400 rounded-xl border border-rose-500/20">
            <Stamp className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100">
              📄 自訂範本審查報告匯出 (Customized DOCX / PDF Report Exporter)
            </h2>
            <p className="text-xs text-slate-400">
              產生符合企業標準版型、包含主管與工程師電子簽核欄位與完整 Audit Trail 之技術報告
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-teal-400" />
            <h3 className="text-base font-bold text-slate-200">Word (.docx) 格式審查報告</h3>
          </div>
          <p className="text-xs text-slate-400">
            包含高階變更統計表、工安數值高紅對照清單、頁碼對照段落與可編輯之簽核簽名欄。
          </p>

          <button
            onClick={handleDocxClick}
            disabled={isExporting}
            className="w-full py-2.5 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-700 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-teal-950/40 flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            {isExporting ? '生成中...' : '靜態匯出 / 下載 DOCX 審查報告'}
          </button>
        </div>

        <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Stamp className="w-5 h-5 text-rose-400" />
            <h3 className="text-base font-bold text-slate-200">HTML / PDF 簽核報告</h3>
          </div>
          <p className="text-xs text-slate-400">
            獨立 HTML / PDF 格式，支援直印與電子數位簽章，包含未覆核防誤警示印章。
          </p>

          <button
            onClick={() => {
              window.open('/api/export-html', '_blank');
            }}
            className="w-full py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-rose-950/40 flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            預覽 / 下載 HTML/PDF 報告
          </button>
        </div>
      </div>
    </div>
  );
};

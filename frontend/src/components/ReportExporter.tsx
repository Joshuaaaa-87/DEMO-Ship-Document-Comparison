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
    <div className="bg-white border border-slate-200 rounded-lg p-5 space-y-4 shadow-xs">
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-rose-50 text-rose-700 rounded border border-rose-200">
            <Stamp className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">
              📄 自訂範本審查報告匯出 (Customized DOCX / PDF Exporter)
            </h2>
            <p className="text-xs text-slate-500">
              產出符合驗船協會與企業標準版型、包含主管與工程師簽核欄位與完整 Audit Trail 之報告
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-teal-700" />
            <h3 className="text-xs font-bold text-slate-800">Word (.docx) 格式審查報告</h3>
          </div>
          <p className="text-xs text-slate-500">
            包含高階變更統計表、工安數值高紅對照清單、頁碼對照段落與可編輯之簽核簽名欄。
          </p>

          <button
            onClick={handleDocxClick}
            disabled={isExporting}
            className="w-full py-2 bg-teal-700 hover:bg-teal-600 disabled:bg-slate-300 text-white rounded text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            {isExporting ? '生成中...' : '靜態匯出 / 下載 DOCX 審查報告'}
          </button>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Stamp className="w-4 h-4 text-rose-700" />
            <h3 className="text-xs font-bold text-slate-800">HTML / PDF 簽核報告</h3>
          </div>
          <p className="text-xs text-slate-500">
            獨立 HTML / PDF 格式，支援直印與電子數位簽章，包含未覆核防誤警示印章。
          </p>

          <button
            onClick={() => {
              window.open('/api/export-html', '_blank');
            }}
            className="w-full py-2 bg-rose-700 hover:bg-rose-600 text-white rounded text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-2"
          >
            <Download className="w-4 h-4" />
            預覽 / 下載 HTML/PDF 報告
          </button>
        </div>
      </div>
    </div>
  );
};

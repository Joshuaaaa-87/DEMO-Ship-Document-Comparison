import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { NotebookLMDifferentiator } from './components/NotebookLMDifferentiator';
import { ManagerDashboard } from './components/ManagerDashboard';
import { EngineerDashboard } from './components/EngineerDashboard';
import { MultiVersionTimeline } from './components/MultiVersionTimeline';
import { SlidesMindmapViewer } from './components/SlidesMindmapViewer';
import { ReportExporter } from './components/ReportExporter';
import { FloatingChatDrawer } from './components/FloatingChatDrawer';
import type { Difference, DocMetadata, Role } from './types';
import { Play } from 'lucide-react';

export default function App() {
  const [role, setRole] = useState<Role>('engineer');
  const [activeTab, setActiveTab] = useState<'comparison' | 'timeline' | 'slides-mindmap' | 'differentiator'>('comparison');
  const [provider, setProvider] = useState<string>('AWS Bedrock (Claude 3.5 Sonnet)');

  const [differences, setDifferences] = useState<Difference[]>([]);
  const [oldMeta, setOldMeta] = useState<DocMetadata>({ title: '', version: 'v1.0', date: '', is_complete: true, missing_fields: [] });
  const [newMeta, setNewMeta] = useState<DocMetadata>({ title: '', version: 'v1.1', date: '', is_complete: true, missing_fields: [] });
  const [scannedOld, setScannedOld] = useState<number[]>([]);
  const [scannedNew, setScannedNew] = useState<number[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    loadDemoData();
  }, []);

  const loadDemoData = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/demo-data?provider=${encodeURIComponent(provider)}`);
      if (res.ok) {
        const data = await res.json();
        setDifferences(data.differences || []);
        setOldMeta(data.old_meta || { title: 'Main Engine Cooling Procedure', version: 'v1.0', date: '2026-08-15' });
        setNewMeta(data.new_meta || { title: 'Main Engine Cooling Procedure', version: 'v1.1', date: '2026-08-15' });
        setScannedOld(data.scanned_old || []);
        setScannedNew(data.scanned_new || []);
      }
    } catch (err) {
      console.error('Failed to load demo data', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateDifference = (id: string, review_status: Difference['review_status'], reviewer_note: string) => {
    setDifferences((prev) =>
      prev.map((d) => (d.id === id ? { ...d, review_status, reviewer_note } : d))
    );
  };

  const handleExportDocx = async () => {
    try {
      const res = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          differences,
          old_version: oldMeta.version || 'v1.0',
          new_version: newMeta.version || 'v1.1',
        }),
      });

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ship-document-diff-report-${oldMeta.version}-vs-${newMeta.version}.docx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      alert('無法導出 DOCX 報告：' + err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans relative">
      
      {/* V1 Light Style Header */}
      <Header
        role={role}
        onRoleChange={setRole}
        provider={provider}
        onProviderChange={setProvider}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Action Controls (Matching V1 Layout) */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 flex flex-wrap items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3">
            <button
              onClick={loadDemoData}
              disabled={isLoading}
              className="px-4 py-2 bg-teal-700 hover:bg-teal-600 text-white rounded font-bold text-xs transition-all shadow-xs flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              {isLoading ? '比對中...' : '載入 6 頁合成 Demo 比對'}
            </button>
            <span className="text-xs text-slate-500">
              分析引擎：<strong className="text-teal-700 font-semibold">{provider}</strong>
            </span>
          </div>

          <div className="text-xs text-slate-500">
            提取可追溯差異：<strong className="text-teal-700 font-bold">{differences.length} 筆</strong>
          </div>
        </div>

        {/* Document Information Cards (Matching V1 Streamlit Dual Light Cards #f0f7f6) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-teal-50/60 border border-teal-200 rounded-lg p-3.5 text-xs space-y-1 text-slate-800 shadow-xs">
            <div className="font-bold text-teal-900">
              <strong>舊版文件：</strong> {oldMeta.title || 'Main Engine Cooling Procedure'}
            </div>
            <div className="text-slate-600">
              <strong>版本號：</strong> <span className="text-teal-700 font-mono font-bold">{oldMeta.version || 'v1.0'}</span> ｜ 
              <strong> 發布日期：</strong> {oldMeta.date || '2026-08-15'} ｜ 
              <strong> 總頁數：</strong> 3 頁
            </div>
          </div>

          <div className="bg-teal-50/60 border border-teal-200 rounded-lg p-3.5 text-xs space-y-1 text-slate-800 shadow-xs">
            <div className="font-bold text-teal-900">
              <strong>新版文件：</strong> {newMeta.title || 'Main Engine Cooling Procedure'}
            </div>
            <div className="text-slate-600">
              <strong>版本號：</strong> <span className="text-teal-700 font-mono font-bold">{newMeta.version || 'v1.1'}</span> ｜ 
              <strong> 發布日期：</strong> {newMeta.date || '2026-08-15'} ｜ 
              <strong> 總頁數：</strong> 3 頁
            </div>
          </div>
        </div>

        {/* Tab View Switching */}
        {activeTab === 'differentiator' && <NotebookLMDifferentiator />}
        {activeTab === 'timeline' && <MultiVersionTimeline />}
        {activeTab === 'slides-mindmap' && (
          <SlidesMindmapViewer provider={provider} differences={differences} />
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-6">
            {role === 'manager' ? (
              <ManagerDashboard
                differences={differences}
                onExportDocx={handleExportDocx}
              />
            ) : (
              <EngineerDashboard
                differences={differences}
                onUpdateDifference={handleUpdateDifference}
                scannedOld={scannedOld}
                scannedNew={scannedNew}
              />
            )}

            <ReportExporter
              differences={differences}
              onExportDocx={handleExportDocx}
            />
          </div>
        )}
      </main>

      {/* Floating 🚢 Ship Chat Drawer Component */}
      <FloatingChatDrawer
        differences={differences}
        provider={provider}
        onProviderChange={setProvider}
      />

      <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-500 bg-white">
        AI 船舶技術文件版本差異 Agent • S1000D 精準對照與審查簽核
      </footer>
    </div>
  );
}

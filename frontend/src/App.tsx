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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans relative">
      
      {/* Clean Header Bar */}
      <Header
        role={role}
        onRoleChange={setRole}
        provider={provider}
        onProviderChange={setProvider}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Container with Spacious Spacing */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Simple Action Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={loadDemoData}
              disabled={isLoading}
              className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg text-xs font-semibold transition-all shadow-sm flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              {isLoading ? '載入數據中...' : '載入 Demo 比對數據'}
            </button>
            <span className="text-xs text-slate-400">
              Demo PDF：<span className="text-slate-300 font-mono">Main_Engine_Cooling_v1.0.pdf</span> vs <span className="text-slate-300 font-mono">v1.1.pdf</span>
            </span>
          </div>

          <div className="text-xs text-slate-400">
            已載入條文差異：<strong className="text-teal-400 font-bold">{differences.length} 筆</strong>
          </div>
        </div>

        {/* Tab View Switching */}
        {activeTab === 'differentiator' && <NotebookLMDifferentiator />}
        {activeTab === 'timeline' && <MultiVersionTimeline />}
        {activeTab === 'slides-mindmap' && (
          <SlidesMindmapViewer provider={provider} differences={differences} />
        )}

        {activeTab === 'comparison' && (
          <div className="space-y-8">
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

      <footer className="border-t border-slate-800/80 py-4 text-center text-xs text-slate-500">
        AI 船舶技術文件版本差異 Agent • S1000D 精準對照與審查簽核
      </footer>
    </div>
  );
}

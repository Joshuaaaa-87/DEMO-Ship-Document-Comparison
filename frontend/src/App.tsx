import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { NotebookLMDifferentiator } from './components/NotebookLMDifferentiator';
import { ManagerDashboard } from './components/ManagerDashboard';
import { EngineerDashboard } from './components/EngineerDashboard';
import { MultiVersionTimeline } from './components/MultiVersionTimeline';
import { ReportExporter } from './components/ReportExporter';
import type { Difference, DocMetadata, Role } from './types';
import { MessageSquare, Play, Send } from 'lucide-react';

export default function App() {
  const [role, setRole] = useState<Role>('engineer');
  const [activeTab, setActiveTab] = useState<'comparison' | 'timeline' | 'differentiator'>('comparison');
  const [provider, setProvider] = useState<string>('OpenAI (default)');
  const [apiKey, setApiKey] = useState<string>('');
  const [language, setLanguage] = useState<string>('繁中');

  const [differences, setDifferences] = useState<Difference[]>([]);
  const [oldMeta, setOldMeta] = useState<DocMetadata>({ title: '', version: 'v1.0', date: '', is_complete: true, missing_fields: [] });
  const [newMeta, setNewMeta] = useState<DocMetadata>({ title: '', version: 'v1.1', date: '', is_complete: true, missing_fields: [] });
  const [scannedOld, setScannedOld] = useState<number[]>([]);
  const [scannedNew, setScannedNew] = useState<number[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);
  const [chatQuestion, setChatQuestion] = useState<string>('');
  const [isChatSending, setIsChatSending] = useState<boolean>(false);

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

  const handleSendChat = async () => {
    if (!chatQuestion.trim()) return;
    const q = chatQuestion.trim();
    setChatQuestion('');
    setChatMessages((prev) => [...prev, { role: 'user', content: q }]);
    setIsChatSending(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, differences, language }),
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [...prev, { role: 'assistant', content: data.answer }]);
      }
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: '對不起，無法檢索回答。' }]);
    } finally {
      setIsChatSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        role={role}
        onRoleChange={setRole}
        provider={provider}
        onProviderChange={setProvider}
        apiKey={apiKey}
        onApiKeyChange={setApiKey}
        language={language}
        onLanguageChange={setLanguage}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={loadDemoData}
              disabled={isLoading}
              className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              {isLoading ? '載入中...' : '載入 6 頁合成 Demo'}
            </button>
            <span className="text-xs text-slate-400">
              Demo PDF：Main_Engine_Cooling_v1.0.pdf vs v1.1.pdf
            </span>
          </div>

          <div className="text-xs text-slate-400">
            全域可追溯差異：<strong className="text-teal-400 font-bold">{differences.length} 筆</strong>
          </div>
        </div>

        {activeTab === 'differentiator' && <NotebookLMDifferentiator />}
        {activeTab === 'timeline' && <MultiVersionTimeline />}

        {activeTab === 'comparison' && (
          <div className="space-y-8">
            <NotebookLMDifferentiator />

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

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <h3 className="text-base font-bold text-slate-200 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-teal-400" />
                詢問文件與差異內容 (RAG 自然語言問答)
              </h3>

              <div className="space-y-3 max-h-80 overflow-y-auto p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
                {chatMessages.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">
                    例如提問：「哪些變更影響冷卻系統？為何 D01 為 High Risk？」
                  </p>
                ) : (
                  chatMessages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl text-xs ${
                        msg.role === 'user'
                          ? 'bg-teal-900/40 text-teal-200 border border-teal-500/30 ml-8'
                          : 'bg-slate-800 text-slate-200 border border-slate-700 mr-8'
                      }`}
                    >
                      <strong className="block text-[10px] text-slate-400 uppercase mb-1">
                        {msg.role === 'user' ? '使用者 (User)' : 'AI Agent 助手 (帶可追溯引用)'}
                      </strong>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>
                  ))
                )}
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                  placeholder="輸入關於技術文件變更之提問..."
                  className="flex-1 bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-4 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
                <button
                  onClick={handleSendChat}
                  disabled={isChatSending}
                  className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-1.5"
                >
                  <Send className="w-4 h-4" />
                  提問
                </button>
              </div>
            </div>

          </div>
        )}
      </main>

      <footer className="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        AI 船舶技術文件版本差異 Agent • Vite + React + Tailwind CSS × FastAPI 引擎
      </footer>
    </div>
  );
}

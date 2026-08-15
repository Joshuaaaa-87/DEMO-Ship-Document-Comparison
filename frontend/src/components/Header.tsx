import React from 'react';
import { Anchor, ShieldCheck, Wrench } from 'lucide-react';
import type { Role } from '../types';

interface HeaderProps {
  role: Role;
  onRoleChange: (newRole: Role) => void;
  provider: string;
  onProviderChange: (provider: string) => void;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  language: string;
  onLanguageChange: (lang: string) => void;
  activeTab: 'comparison' | 'timeline' | 'slides-mindmap' | 'differentiator';
  onTabChange: (tab: 'comparison' | 'timeline' | 'slides-mindmap' | 'differentiator') => void;
}

export const Header: React.FC<HeaderProps> = ({
  role,
  onRoleChange,
  provider,
  onProviderChange,
  activeTab,
  onTabChange,
}) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-600/20 text-teal-400 rounded-xl border border-teal-500/30">
              <Anchor className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-teal-400 to-cyan-300 bg-clip-text text-transparent">
                AI 船舶技術文件版本差異 Agent
              </h1>
              <p className="text-xs text-slate-400 hidden sm:block">
                S1000D 100% 可追溯對照 • 工安數值警示 • 人工審查簽核
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center bg-slate-800/80 p-1 rounded-xl border border-slate-700/50">
            <button
              onClick={() => onTabChange('comparison')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'comparison'
                  ? 'bg-teal-600 text-white shadow-lg shadow-teal-900/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              單對比審查視圖
            </button>
            <button
              onClick={() => onTabChange('timeline')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'timeline'
                  ? 'bg-teal-600 text-white shadow-lg shadow-teal-900/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📊 3~5 版演進時間軸
            </button>
            <button
              onClick={() => onTabChange('slides-mindmap')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'slides-mindmap'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              📽️ Demo 簡報與心智圖
            </button>
            <button
              onClick={() => onTabChange('differentiator')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'differentiator'
                  ? 'bg-amber-600 text-white shadow-lg shadow-amber-900/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              ⚡ 勝過 NotebookLM 差異
            </button>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700/60">
              <button
                onClick={() => onRoleChange('manager')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  role === 'manager'
                    ? 'bg-rose-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="切換至安品/工程主管視圖"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">安品主管</span>
              </button>
              <button
                onClick={() => onRoleChange('engineer')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  role === 'engineer'
                    ? 'bg-teal-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="切換至第一線維修工程師視圖"
              >
                <Wrench className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">維修工程師</span>
              </button>
            </div>

            <select
              value={provider}
              onChange={(e) => onProviderChange(e.target.value)}
              className="bg-slate-800 text-slate-200 border border-slate-700 rounded-xl px-2.5 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/50"
            >
              <option value="OpenAI (default)">OpenAI (GPT-4o)</option>
              <option value="Gemini">Gemini 1.5 Flash</option>
              <option value="Amazon Bedrock">Amazon Bedrock</option>
              <option value="Groq">Groq Llama-3.3</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};

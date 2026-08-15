import React from 'react';
import { Anchor, ShieldCheck, Wrench } from 'lucide-react';
import type { Role } from '../types';

interface HeaderProps {
  role: Role;
  onRoleChange: (newRole: Role) => void;
  provider: string;
  onProviderChange: (provider: string) => void;
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
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Brand Logo & Title (V1 Streamlit Light Maritime Style) */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-50 text-teal-700 rounded-lg border border-teal-200">
              <Anchor className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-teal-800 tracking-tight">
                AI 船舶技術文件版本差異 Agent
              </h1>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                S1000D 可追溯對照 • 工安語意提醒 • 人工審查簽核
              </p>
            </div>
          </div>

          {/* Clean Segment Tabs (Light Theme) */}
          <nav className="hidden md:flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200">
            <button
              onClick={() => onTabChange('comparison')}
              className={`px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                activeTab === 'comparison'
                  ? 'bg-teal-700 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              條文對照與審查
            </button>
            <button
              onClick={() => onTabChange('timeline')}
              className={`px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                activeTab === 'timeline'
                  ? 'bg-teal-700 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              3~5 版演進時間軸
            </button>
            <button
              onClick={() => onTabChange('slides-mindmap')}
              className={`px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                activeTab === 'slides-mindmap'
                  ? 'bg-teal-700 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              簡報與心智圖
            </button>
            <button
              onClick={() => onTabChange('differentiator')}
              className={`px-3 py-1.5 rounded text-xs font-semibold transition-all ${
                activeTab === 'differentiator'
                  ? 'bg-amber-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              NotebookLM 差異定位
            </button>
          </nav>

          {/* Role Switcher & Model Selector */}
          <div className="flex items-center gap-3">
            
            {/* Role Switcher */}
            <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
              <button
                onClick={() => onRoleChange('manager')}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-semibold transition-all ${
                  role === 'manager'
                    ? 'bg-rose-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="切換至安品主管視圖"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>安品主管</span>
              </button>
              <button
                onClick={() => onRoleChange('engineer')}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-semibold transition-all ${
                  role === 'engineer'
                    ? 'bg-teal-700 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="切換至維修工程師視圖"
              >
                <Wrench className="w-3.5 h-3.5" />
                <span>維修工程師</span>
              </button>
            </div>

            {/* Model Selector */}
            <select
              value={provider}
              onChange={(e) => onProviderChange(e.target.value)}
              className="bg-white text-slate-700 border border-slate-300 rounded-lg px-2.5 py-1 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-teal-500 shadow-xs"
            >
              <option value="AWS Bedrock (Claude 3.5 Sonnet)">AWS Bedrock (Claude 3.5)</option>
              <option value="OpenAI (default)">ChatGPT (GPT-4o)</option>
              <option value="Gemini">Gemini 1.5 Flash</option>
            </select>

          </div>
        </div>
      </div>
    </header>
  );
};

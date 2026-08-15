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
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-teal-500/10 text-teal-400 rounded-lg border border-teal-500/20">
              <Anchor className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-100 tracking-tight">
                AI 船舶技術文件版本差異 Agent
              </h1>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                S1000D 頁碼對照 • 工安數值標紅 • 審查簽核
              </p>
            </div>
          </div>

          {/* Clean Segment Tabs */}
          <nav className="hidden md:flex items-center bg-slate-800/60 p-1 rounded-lg border border-slate-700/50">
            <button
              onClick={() => onTabChange('comparison')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'comparison'
                  ? 'bg-teal-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              條文對照審查
            </button>
            <button
              onClick={() => onTabChange('timeline')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'timeline'
                  ? 'bg-teal-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              3~5 版演進時間軸
            </button>
            <button
              onClick={() => onTabChange('slides-mindmap')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'slides-mindmap'
                  ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              簡報與心智圖
            </button>
            <button
              onClick={() => onTabChange('differentiator')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                activeTab === 'differentiator'
                  ? 'bg-amber-600 text-white font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              產品優勢與定位
            </button>
          </nav>

          {/* Role Switcher & Model Selector */}
          <div className="flex items-center gap-3">
            
            {/* Role Switcher */}
            <div className="flex items-center bg-slate-800/80 p-0.5 rounded-lg border border-slate-700">
              <button
                onClick={() => onRoleChange('manager')}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                  role === 'manager'
                    ? 'bg-rose-600 text-white shadow-xs'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="切換至安品主管視圖"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>安品主管</span>
              </button>
              <button
                onClick={() => onRoleChange('engineer')}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                  role === 'engineer'
                    ? 'bg-teal-600 text-white shadow-xs'
                    : 'text-slate-400 hover:text-slate-200'
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
              className="bg-slate-800 text-slate-300 border border-slate-700 rounded-lg px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
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

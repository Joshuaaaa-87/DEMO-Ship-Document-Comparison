import React, { useState } from 'react';
import { Anchor, X, Send, Bot } from 'lucide-react';
import type { Difference } from '../types';

interface FloatingChatDrawerProps {
  differences: Difference[];
  provider: string;
  onProviderChange: (p: string) => void;
}

export const FloatingChatDrawer: React.FC<FloatingChatDrawerProps> = ({
  differences,
  provider,
  onProviderChange,
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([
    {
      role: 'assistant',
      content: '👋 哈囉！我是 AI 船舶技術文件助手。您可以向我詢問手冊條文變更、S1000D 原始段落引用或工安風險評估細節。',
    },
  ]);
  const [question, setQuestion] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);

  const handleSend = async () => {
    if (!question.trim()) return;
    const q = question.trim();
    setQuestion('');
    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setIsSending(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, differences, language: '繁中', provider }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '對不起，目前無法取得對話檢索回答。' },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <>
      {/* Floating 🚢 Ship Action Button at Bottom Right */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 p-3.5 bg-teal-700 hover:bg-teal-600 text-white rounded-full shadow-lg border border-teal-500 flex items-center gap-2 transition-all duration-300 transform hover:scale-105"
        title="開啟 🚢 AI 助手 (帶可追溯引用對話)"
      >
        <Anchor className="w-5 h-5 animate-pulse" />
        <span className="text-xs font-bold pr-1">🚢 AI 助手</span>
        <span className="absolute -top-1 -right-1 flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-teal-300"></span>
        </span>
      </button>

      {/* Slide-over Right Drawer Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
          <div className="w-full max-w-md bg-white border-l border-slate-200 shadow-2xl flex flex-col h-full animate-in slide-in-from-right duration-300">
            
            {/* Drawer Header */}
            <div className="p-4 border-b border-slate-200 bg-teal-50 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-teal-100 text-teal-800 rounded border border-teal-200">
                  <Anchor className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-teal-900 flex items-center gap-1.5">
                    🚢 AI 助手 (帶可追溯引用)
                  </h3>
                  <p className="text-[11px] text-teal-700">
                    S1000D 精準對照問答
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-200 transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Model Switcher Bar */}
            <div className="px-4 py-2 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs">
              <span className="text-slate-600 flex items-center gap-1">
                <Bot className="w-3.5 h-3.5 text-teal-700" />
                AI 模型調度：
              </span>
              <select
                value={provider}
                onChange={(e) => onProviderChange(e.target.value)}
                className="bg-white text-slate-700 border border-slate-300 rounded px-2 py-1 text-[11px] font-semibold focus:outline-none focus:ring-1 focus:ring-teal-500 shadow-xs"
              >
                <option value="AWS Bedrock (Claude 3.5 Sonnet)">AWS Bedrock Claude 3.5</option>
                <option value="OpenAI (default)">ChatGPT GPT-4o</option>
                <option value="Gemini">Gemini 1.5 Flash</option>
              </select>
            </div>

            {/* Messages Body */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50/50">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg text-xs space-y-1 ${
                    msg.role === 'user'
                      ? 'bg-teal-700 text-white ml-8 shadow-xs'
                      : 'bg-white text-slate-800 border border-slate-200 mr-8 shadow-xs'
                  }`}
                >
                  <div className={`text-[10px] font-bold uppercase tracking-wider ${msg.role === 'user' ? 'text-teal-200' : 'text-slate-500'}`}>
                    {msg.role === 'user' ? '使用者 (User)' : 'AI 船舶 Agent'}
                  </div>
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                </div>
              ))}
            </div>

            {/* Input Footer */}
            <div className="p-4 border-t border-slate-200 bg-white">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="輸入關於條文變更、工安風險之提問..."
                  className="flex-1 bg-white text-slate-800 border border-slate-300 rounded px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500 shadow-xs"
                />
                <button
                  onClick={handleSend}
                  disabled={isSending}
                  className="px-3.5 py-2 bg-teal-700 hover:bg-teal-600 text-white rounded text-xs font-bold transition-all flex items-center justify-center gap-1 shadow-xs"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

          </div>
        </div>
      )}
    </>
  );
};

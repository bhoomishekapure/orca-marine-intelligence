import React, { useState, useRef, useEffect } from 'react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'orca';
  text: string;
  intent?: string;
  language?: string;
  timestamp: string;
  executionMs?: number;
}

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (query: string) => void;
  isLoading: boolean;
}

const QUICK_PROMPTS = [
  { label: 'Flow 1: Marine Safety (6 AM)', query: 'Is it safe to go fishing tomorrow at 6 AM near Ratnagiri?' },
  { label: 'Flow 2: Nearest PFZ Zone', query: 'Where is the nearest Potential Fishing Zone?' },
  { label: 'Flow 3: Sea Conditions', query: 'What are the sea conditions near Ratnagiri tomorrow morning?' },
  { label: 'Flow 4: Follow-up (9 AM)', query: 'What about 9 AM instead?' },
  { label: 'Flow 5: मराठी प्रश्न (Safety)', query: 'उद्या सकाळी रत्नागिरीजवळ मासेमारीसाठी समुद्रात जाणे सुरक्षित आहे का?' }
];

export const ChatPanel: React.FC<ChatPanelProps> = ({ messages, onSendMessage, isLoading }) => {
  const [inputQuery, setInputQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;
    onSendMessage(inputQuery.trim());
    setInputQuery('');
  };

  return (
    <div className="flex flex-col h-full bg-ocean-900 border border-ocean-700 rounded-xl overflow-hidden shadow-xl">
      {/* Panel Header */}
      <div className="bg-ocean-850 px-4 py-2.5 border-b border-ocean-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Conversational Marine Intelligence
          </h2>
        </div>
        <span className="text-[11px] text-slate-400">Multi-turn Memory Active</span>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="p-2.5 bg-ocean-950/60 border-b border-ocean-800 flex items-center gap-1.5 overflow-x-auto no-scrollbar">
        <span className="text-[10px] uppercase font-bold text-slate-400 shrink-0">Demo Scenarios:</span>
        {QUICK_PROMPTS.map((qp, idx) => (
          <button
            key={idx}
            onClick={() => onSendMessage(qp.query)}
            disabled={isLoading}
            className="shrink-0 px-2 py-1 rounded bg-ocean-850 hover:bg-ocean-700 text-cyan-300 text-[11px] border border-ocean-700/80 transition-colors disabled:opacity-50"
          >
            {qp.label}
          </button>
        ))}
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed shadow-md ${
                msg.sender === 'user'
                  ? 'bg-gradient-to-r from-ocean-600 to-ocean-500 text-white rounded-br-none'
                  : 'bg-ocean-850 border border-ocean-700 text-slate-200 rounded-bl-none'
              }`}
            >
              {msg.text}
            </div>
            <div className="flex items-center gap-2 mt-1 px-1 text-[10px] text-slate-400">
              <span>{msg.timestamp}</span>
              {msg.intent && (
                <span className="px-1.5 py-0.2 rounded bg-ocean-800 text-cyan-400 font-mono">
                  {msg.intent}
                </span>
              )}
              {msg.executionMs && (
                <span className="font-mono text-slate-500">
                  {msg.executionMs} ms
                </span>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start">
            <div className="bg-ocean-850 border border-ocean-700 rounded-2xl rounded-bl-none px-4 py-3 text-xs text-slate-300 flex items-center gap-2 shadow-md">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" />
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]" />
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]" />
              <span className="text-[11px] text-slate-400 font-mono ml-2">Reasoning with specialized agents...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-3 bg-ocean-850 border-t border-ocean-700 flex items-center gap-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask ORCA in English, Marathi, or Hindi... (e.g. Is fishing safe tomorrow at 6 AM?)"
          disabled={isLoading}
          className="flex-1 bg-ocean-950 border border-ocean-700 rounded-lg px-3.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={isLoading || !inputQuery.trim()}
          className="bg-ocean-500 hover:bg-ocean-400 text-white font-semibold text-xs px-4 py-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 shadow-md shadow-ocean-500/20"
        >
          <span>Send</span>
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  );
};

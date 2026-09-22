'use client';

import React, { useState } from 'react';
import { Mic, FileText, Send, Languages, Sparkles, UploadCloud } from 'lucide-react';
import { api } from '@/lib/api';
import { QueryResponse } from '@/lib/types';
import VoiceInput from './VoiceInput';

interface Props {
  onResult: (res: QueryResponse) => void;
  setLoading: (l: boolean) => void;
  loading: boolean;
  setStage: (s: number) => void;
}

const INDIAN_LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
  { code: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { code: 'ml', label: 'മലയാളം (Malayalam)' },
];

const SAMPLE_QUERIES = [
  { label: 'Drinking Water Quality', q: 'What is the permissible limit for total dissolved solids in drinking water under IS 10500?' },
  { label: 'Packaged Water (Hindi)', q: 'इस उत्पाद के लिए कौन सा BIS मानक लागू है?' },
  { label: 'Helmet Safety (Tamil)', q: 'இந்த தயாரிப்பிற்கு எந்த BIS தரநிலை பொருந்தும்?' },
  { label: 'Two-Wheeler Helmets', q: 'What are the impact absorption test requirements under IS 4151:2015?' }
];

export default function QueryAssistant({ onResult, setLoading, loading, setStage }: Props) {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState('en');
  const [mode, setMode] = useState<'text' | 'voice' | 'doc'>('text');
  const [attachedDoc, setAttachedDoc] = useState<File | null>(null);

  const simulateStages = () => {
    setStage(1);
    const t1 = setTimeout(() => setStage(3), 600);
    const t2 = setTimeout(() => setStage(5), 1400);
    const t3 = setTimeout(() => setStage(7), 2200);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() && mode !== 'voice') return;

    setLoading(true);
    const cleanupStages = simulateStages();

    try {
      let res: QueryResponse;
      if (mode === 'doc' && attachedDoc) {
        res = await api.submitDocumentQuery(attachedDoc, query, language);
      } else {
        res = await api.submitQuery(query, language);
      }
      setStage(8);
      onResult(res);
    } catch (err: any) {
      console.error('Query failed:', err);
    } finally {
      cleanupStages();
      setLoading(false);
    }
  };

  const handleVoiceSubmit = async (file: File) => {
    setLoading(true);
    const cleanupStages = simulateStages();
    try {
      const res = await api.submitVoiceQuery(file, language);
      setStage(8);
      onResult(res);
    } catch (err) {
      console.error('Voice query failed:', err);
    } finally {
      cleanupStages();
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* Query Mode Switcher */}
      <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-700/60">
        <button
          type="button"
          onClick={() => setMode('text')}
          className={`flex-1 py-2 text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1.5 ${
            mode === 'text' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" /> Text Query
        </button>
        <button
          type="button"
          onClick={() => setMode('voice')}
          className={`flex-1 py-2 text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1.5 ${
            mode === 'voice' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Mic className="w-3.5 h-3.5" /> Voice Query
        </button>
        <button
          type="button"
          onClick={() => setMode('doc')}
          className={`flex-1 py-2 text-xs font-semibold rounded-lg transition flex items-center justify-center gap-1.5 ${
            mode === 'doc' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3.5 h-3.5" /> Document Query
        </button>
      </div>

      {/* Language Selector */}
      <div className="flex items-center justify-between bg-slate-900/60 px-3 py-2 rounded-xl border border-slate-700/60 text-xs">
        <div className="flex items-center gap-2 text-slate-400">
          <Languages className="w-4 h-4 text-blue-400" />
          <span>Select Query Language:</span>
        </div>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="bg-slate-800 text-slate-200 font-medium px-2 py-1 rounded-lg border border-slate-700 outline-none cursor-pointer focus:border-blue-500"
        >
          {INDIAN_LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.label}
            </option>
          ))}
        </select>
      </div>

      {/* Input depending on mode */}
      {mode === 'voice' ? (
        <div className="p-6 border border-dashed border-slate-700 rounded-xl bg-slate-900/40 flex flex-col items-center justify-center gap-3">
          <p className="text-xs text-slate-400 text-center">
            Click record to speak your question in English or any Indian language. IndicBERT will transcribe and analyze intent.
          </p>
          <VoiceInput onVoiceRecorded={handleVoiceSubmit} disabled={loading} />
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {mode === 'doc' && (
            <div className="p-3 bg-slate-900/60 border border-slate-700/70 rounded-xl flex items-center justify-between">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <UploadCloud className="w-4 h-4 text-emerald-400" />
                <span>{attachedDoc ? attachedDoc.name : 'Attach Product Spec / PDF to Query'}</span>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) setAttachedDoc(e.target.files[0]);
                  }}
                />
              </label>
              {attachedDoc && (
                <button
                  type="button"
                  onClick={() => setAttachedDoc(null)}
                  className="text-xs text-rose-400 hover:underline"
                >
                  Remove
                </button>
              )}
            </div>
          )}

          <textarea
            rows={4}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              language === 'hi'
                ? 'इस उत्पाद के लिए कौन सा BIS मानक लागू है?'
                : language === 'ta'
                ? 'இந்த தயாரிப்பிற்கு எந்த BIS தரநிலை பொருந்தும்?'
                : 'Ask your BIS regulatory question (e.g. What standard applies to packaged drinking water?)...'
            }
            className="w-full bg-slate-900/80 border border-slate-700 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none transition"
          />
        </div>
      )}

      {/* Quick Prompts */}
      <div className="flex flex-wrap gap-1.5">
        <span className="text-[11px] text-slate-500 font-medium mr-1 py-0.5">Quick Examples:</span>
        {SAMPLE_QUERIES.map((sq, i) => (
          <button
            key={i}
            type="button"
            onClick={() => setQuery(sq.q)}
            className="text-[11px] bg-slate-800/80 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700/60 transition truncate max-w-[200px]"
            title={sq.q}
          >
            {sq.label}
          </button>
        ))}
      </div>

      {mode !== 'voice' && (
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 transition"
        >
          <Send className="w-4 h-4" />
          {loading ? 'Orchestrating 10-Stage RDA...' : 'Submit BIS Query'}
        </button>
      )}
    </form>
  );
}

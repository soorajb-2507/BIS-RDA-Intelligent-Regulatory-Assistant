import React from 'react';
import { BookMarked, ExternalLink, Hash, FileText } from 'lucide-react';
import { EvidenceItem } from '@/lib/types';

interface Props {
  evidence: EvidenceItem[];
  sources: string[];
}

export default function EvidenceCard({ evidence, sources }: Props) {
  if (!evidence || evidence.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BookMarked className="w-5 h-5 text-indigo-400" />
          <h3 className="text-md font-bold text-white">Retrieved & Verified BIS Evidence</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {evidence.length} Verified Evidence Block{evidence.length > 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-4">
        {evidence.map((item, idx) => (
          <div
            key={idx}
            className="bg-slate-900/70 border border-slate-700/80 rounded-xl p-4 transition hover:border-slate-600"
          >
            {/* Metadata Tags */}
            <div className="flex flex-wrap items-center gap-2 mb-2 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/30 font-semibold flex items-center gap-1">
                <FileText className="w-3 h-3" /> {item.document}
              </span>

              <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
                <Hash className="w-3 h-3" /> Clause: {item.clause}
              </span>

              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Page {item.page}
              </span>

              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                Ver {item.version}
              </span>

              <span className="ml-auto text-emerald-400 font-sans font-medium text-[10px]">
                Match: {(item.relevance_score * 100).toFixed(0)}%
              </span>
            </div>

            {/* Evidence Snippet */}
            <p className="text-xs text-slate-300 leading-relaxed font-sans bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
              "{item.snippet}"
            </p>
          </div>
        ))}
      </div>

      {/* Source References */}
      {sources && sources.length > 0 && (
        <div className="mt-6 pt-4 border-t border-slate-700/60">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
            <ExternalLink className="w-3.5 h-3.5 text-blue-400" />
            <span>Official Source References</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {sources.map((src, i) => (
              <span
                key={i}
                className="text-xs bg-slate-900/80 px-2.5 py-1 rounded-md text-slate-400 border border-slate-800 font-mono"
              >
                {src}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

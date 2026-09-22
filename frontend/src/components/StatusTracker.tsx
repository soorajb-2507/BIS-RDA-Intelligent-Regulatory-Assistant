import React from 'react';
import { CheckCircle2, CircleDashed } from 'lucide-react';

interface Props {
  currentStage: number;
}

const STAGES = [
  'User Query Received',
  'IndicBERT NLP & Intent',
  'RDA Regulatory Mapping',
  'Hybrid Retrieval (ES + Qdrant + Neo4j)',
  'LlamaIndex Context Construction',
  'Ollama (Qwen/Llama) Reasoning',
  'Evidence Verification',
  'Final Explainable Output'
];

export default function StatusTracker({ currentStage }: Props) {
  return (
    <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4 my-3">
      <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-3">
        10-Stage RDA Processing Pipeline
      </h4>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentStage;
          const isCurrent = idx === currentStage;
          return (
            <div
              key={stage}
              className={`p-2 rounded-lg border text-[11px] flex items-center gap-2 ${
                isDone
                  ? 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
                  : isCurrent
                  ? 'bg-blue-950/40 border-blue-500/50 text-blue-300 animate-pulse'
                  : 'bg-slate-900/40 border-slate-800 text-slate-500'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              ) : (
                <CircleDashed className={`w-3.5 h-3.5 shrink-0 ${isCurrent ? 'animate-spin text-blue-400' : ''}`} />
              )}
              <span className="truncate">{stage}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, ThumbsUp, ThumbsDown, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface Props {
  answer: string;
  verified: boolean;
  notes?: string | null;
  queryId?: number;
}

export default function AnswerDisplay({ answer, verified, notes, queryId }: Props) {
  const [feedbackSent, setFeedbackSent] = useState<string | null>(null);

  const handleFeedback = async (type: 'helpful' | 'unhelpful' | 'incorrect') => {
    if (!queryId) return;
    try {
      await api.submitFeedback(queryId, type);
      setFeedbackSent(type);
    } catch (err) {
      console.error('Feedback submission failed:', err);
    }
  };

  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700 rounded-2xl p-6 shadow-xl relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping" />
          <h3 className="text-lg font-bold text-white tracking-wide">AI Regulatory Reasoning Answer</h3>
        </div>

        {verified ? (
          <span className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/40 shadow-sm">
            <CheckCircle2 className="w-4 h-4" /> Evidence Verified
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/40 shadow-sm">
            <AlertTriangle className="w-4 h-4" /> Insufficient Evidence
          </span>
        )}
      </div>

      <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-line bg-slate-900/50 p-4 rounded-xl border border-slate-700/50 font-sans">
        {answer}
      </div>

      {notes && (
        <div className="mt-4 p-3 bg-slate-900/60 rounded-lg border border-slate-700/60 text-xs text-slate-400 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-slate-300">Verification Engine Audit:</span> {notes}
          </div>
        </div>
      )}

      {/* Feedback Mechanism for Continuous Regulatory Learning */}
      {queryId && (
        <div className="mt-4 pt-3 border-t border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
          <span>Continuous Regulatory Learning: Was this verified answer helpful?</span>
          <div className="flex items-center gap-2">
            {feedbackSent ? (
              <span className="text-emerald-400 font-medium">Thank you for your feedback!</span>
            ) : (
              <>
                <button
                  onClick={() => handleFeedback('helpful')}
                  className="px-2.5 py-1 rounded-md bg-slate-900 hover:bg-emerald-950/40 hover:text-emerald-300 border border-slate-700 transition flex items-center gap-1"
                >
                  <ThumbsUp className="w-3 h-3" /> Helpful
                </button>
                <button
                  onClick={() => handleFeedback('unhelpful')}
                  className="px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1"
                >
                  <ThumbsDown className="w-3 h-3" /> Unhelpful
                </button>
                <button
                  onClick={() => handleFeedback('incorrect')}
                  className="px-2.5 py-1 rounded-md bg-slate-900 hover:bg-rose-950/40 hover:text-rose-300 border border-slate-700 transition flex items-center gap-1"
                >
                  Report Discrepancy
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

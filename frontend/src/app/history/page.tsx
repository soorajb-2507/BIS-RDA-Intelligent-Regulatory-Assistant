'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import axios from 'axios';
import { History, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

interface AuditItem {
  id: number;
  query: string;
  language: string;
  intent: string;
  verified: boolean;
  created_at: string;
}

export default function HistoryPage() {
  const [audits, setAudits] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In dev or when direct audits endpoint is queried
    const mockOrFetch = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/standards');
        // If standards return, populate sample audit history for demonstration
        setAudits([
          {
            id: 1,
            query: 'What standard applies to packaged drinking water?',
            language: 'en',
            intent: 'APPLICABLE_STANDARD_INQUIRY',
            verified: true,
            created_at: new Date().toISOString()
          },
          {
            id: 2,
            query: 'इस उत्पाद के लिए कौन सा BIS मानक लागू है?',
            language: 'hi',
            intent: 'APPLICABLE_STANDARD_INQUIRY',
            verified: true,
            created_at: new Date(Date.now() - 3600000).toISOString()
          },
          {
            id: 3,
            query: 'What is the standard for quantum nuclear spacecraft rockets?',
            language: 'en',
            intent: 'GENERAL_REGULATORY_INQUIRY',
            verified: false,
            created_at: new Date(Date.now() - 7200000).toISOString()
          }
        ]);
      } catch (err) {
        console.error('Audit fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    mockOrFetch();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <History className="w-6 h-6 text-indigo-400" />
            <h1 className="text-2xl font-black text-white">Query Audit & Verification History</h1>
          </div>
          <p className="text-xs text-slate-400">
            Audit trail of all regulatory queries, IndicBERT intent classifications, and evidence verification decisions.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
          {loading ? (
            <div className="py-12 text-center text-xs text-slate-500 animate-pulse">
              Loading query audits from PostgreSQL...
            </div>
          ) : audits.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500">
              No query audits recorded yet. Submit queries on the Assistant page to populate this log.
            </div>
          ) : (
            <div className="divide-y divide-slate-800">
              {audits.map((item) => (
                <div key={item.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] uppercase font-bold font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/30">
                        {item.language}
                      </span>
                      <span className="text-xs font-mono text-slate-400">
                        {item.intent}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-slate-200">{item.query}</p>
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(item.created_at).toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="shrink-0">
                    {item.verified ? (
                      <span className="flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        <AlertTriangle className="w-3.5 h-3.5" /> Insufficient Evidence
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

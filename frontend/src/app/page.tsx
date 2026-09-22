'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import QueryAssistant from '@/components/QueryAssistant';
import AnswerDisplay from '@/components/AnswerDisplay';
import EvidenceCard from '@/components/EvidenceCard';
import StandardsPath from '@/components/StandardsPath';
import LabGuidance from '@/components/LabGuidance';
import StatusTracker from '@/components/StatusTracker';
import { QueryResponse } from '@/lib/types';
import { ShieldCheck, Cpu, Database, BookOpen, Layers } from 'lucide-react';

export default function DashboardPage() {
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Navbar />

      {/* Hero Banner */}
      <section className="border-b border-slate-800 bg-gradient-to-b from-slate-900 via-slate-900/60 to-slate-950 px-6 py-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 font-mono text-[11px] font-bold">
                SIH AI Regulatory Platform
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[11px] font-bold">
                IndicBERT + 10-Stage RDA
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              BIS Regulatory & Standards AI Assistant
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl mt-1">
              Ask complex questions regarding Bureau of Indian Standards (BIS) specifications, certification schemes, and laboratory test guidance with verified clause-level evidence.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 p-3 rounded-2xl">
            <div className="text-right">
              <div className="text-xs font-bold text-slate-200">Evidence Verification</div>
              <div className="text-[11px] text-emerald-400 font-mono">Zero Hallucination Mode</div>
            </div>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
        </div>
      </section>

      {/* Main Content Grid */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Query Interface & IndicBERT Metadata */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-2 mb-2">
              <BookOpen className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg font-bold text-white">Ask BIS Question</h2>
            </div>
            <p className="text-xs text-slate-400 mb-5">
              Supports Text, Voice, and Document-based queries across Indian languages (Hindi, Tamil, Telugu, etc.).
            </p>

            <QueryAssistant
              onResult={setQueryResult}
              setLoading={setLoading}
              loading={loading}
              setStage={setStage}
            />
          </div>

          {/* Active Pipeline Status */}
          {loading && <StatusTracker currentStage={stage} />}

          {/* IndicBERT NLP Analysis Card */}
          {queryResult && (
            <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-2xl p-6 shadow-xl">
              <div className="flex items-center gap-2 mb-3">
                <Cpu className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-indigo-300">IndicBERT NLP Extraction</h3>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                  <span className="text-slate-500 block text-[10px] uppercase font-bold mb-0.5">Detected Intent</span>
                  <span className="font-mono text-emerald-400 font-semibold">{queryResult.intent}</span>
                </div>

                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                  <span className="text-slate-500 block text-[10px] uppercase font-bold mb-0.5">Language Detected</span>
                  <span className="font-mono text-blue-400 font-semibold uppercase">{queryResult.language}</span>
                </div>

                <div className="col-span-2 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                  <span className="text-slate-500 block text-[10px] uppercase font-bold mb-0.5">Extracted Entities & Products</span>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {queryResult.entities && queryResult.entities.length > 0 ? (
                      queryResult.entities.map((ent, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 font-mono text-[11px]">
                          {ent}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500 text-xs italic">General Regulatory Search</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Knowledge Store Connectivity Indicators */}
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-4 text-xs">
            <div className="flex items-center gap-2 mb-3 text-slate-400 font-semibold">
              <Layers className="w-4 h-4 text-blue-400" />
              <span>Connected Hybrid Knowledge Stores</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/50 border border-slate-800">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>PostgreSQL (Metadata)</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/50 border border-slate-800">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>Elasticsearch (Lexical)</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/50 border border-slate-800">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>Qdrant (Vectors)</span>
              </div>
              <div className="flex items-center gap-2 p-2 rounded-lg bg-slate-950/50 border border-slate-800">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>Neo4j (Knowledge Graph)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Reasoning, Evidence & Guidance */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          {loading && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center animate-pulse flex flex-col items-center justify-center">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-slate-200 font-bold text-base">Orchestrating RDA 10-Stage Regulatory Reasoning...</p>
              <p className="text-xs text-slate-500 mt-2 max-w-md">
                IndicBERT intent extraction → Hybrid retrieval across Elasticsearch, Qdrant & Neo4j → LlamaIndex context construction → Ollama (Qwen/Llama) evidence-only reasoning → Evidence verification.
              </p>
            </div>
          )}

          {!loading && queryResult && (
            <>
              <AnswerDisplay
                answer={queryResult.answer}
                verified={queryResult.verified}
                notes={queryResult.verification_notes}
                queryId={queryResult.query_id}
              />

              <StandardsPath
                standards={queryResult.applicable_standards}
                paths={queryResult.certification_path}
              />

              <LabGuidance labs={queryResult.testing_guidance} />

              <EvidenceCard
                evidence={queryResult.evidence}
                sources={queryResult.sources}
              />
            </>
          )}

          {!loading && !queryResult && (
            <div className="h-full min-h-[420px] flex flex-col items-center justify-center border-2 border-dashed border-slate-800/80 rounded-2xl p-12 text-center">
              <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-4">
                <ShieldCheck className="w-8 h-8" />
              </div>
              <p className="text-lg font-bold text-slate-300">Ready for BIS Regulatory Query</p>
              <p className="text-xs text-slate-500 max-w-sm mt-1 leading-relaxed">
                Submit a regulatory or compliance query in English, Hindi, Tamil, or other Indian languages. The system will retrieve verified standards and cite exact clauses.
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

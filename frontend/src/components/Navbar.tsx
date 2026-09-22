import React from 'react';
import Link from 'next/link';
import { ShieldCheck, BookOpen, Share2, History, Database } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-amber-500 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-black text-lg tracking-wider text-white">BIS AI ASSISTANT</span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                RDA v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 tracking-tight">Bureau of Indian Standards • Regulatory QA & Verification</p>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-2 text-sm font-medium">
          <Link
            href="/"
            className="px-3.5 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition flex items-center gap-2"
          >
            <BookOpen className="w-4 h-4 text-blue-400" />
            <span>Assistant</span>
          </Link>

          <Link
            href="/documents"
            className="px-3.5 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition flex items-center gap-2"
          >
            <Database className="w-4 h-4 text-emerald-400" />
            <span>Document Ingestion</span>
          </Link>

          <Link
            href="/knowledge-graph"
            className="px-3.5 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition flex items-center gap-2"
          >
            <Share2 className="w-4 h-4 text-amber-400" />
            <span>Knowledge Graph</span>
          </Link>

          <Link
            href="/history"
            className="px-3.5 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/80 transition flex items-center gap-2"
          >
            <History className="w-4 h-4 text-indigo-400" />
            <span>Audit History</span>
          </Link>
        </nav>
      </div>
    </header>
  );
}

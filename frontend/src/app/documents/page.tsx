'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import DocumentUpload from '@/components/DocumentUpload';
import { api } from '@/lib/api';
import { BISDocumentRecord } from '@/lib/types';
import { Database, FileText, CheckCircle2, Clock, RefreshCw } from 'lucide-react';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<BISDocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        <div>
          <h1 className="text-2xl font-black text-white">BIS Document Ingestion & Knowledge Base</h1>
          <p className="text-xs text-slate-400 mt-1">
            Ingest BIS standards, scanned PDFs, guidelines, and amendments into PostgreSQL, Elasticsearch, Qdrant, and Neo4j.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Upload Form */}
          <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl h-fit">
            <h2 className="text-base font-bold text-white mb-1">Upload New Standard / Document</h2>
            <p className="text-xs text-slate-400 mb-6">
              Processed automatically with PyMuPDF and PaddleOCR fallback.
            </p>
            <DocumentUpload onSuccess={fetchDocs} />
          </div>

          {/* Document Status List */}
          <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-white">Ingested BIS Standards & Versions</h2>
              </div>
              <button
                onClick={fetchDocs}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                title="Refresh Documents"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {loading ? (
              <div className="py-12 text-center text-slate-500 text-xs animate-pulse">
                Loading indexed standards from PostgreSQL...
              </div>
            ) : documents.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-xs">
                No documents found. Upload a standard or start the backend to load seed standards.
              </div>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-blue-400">
                          {doc.standard_number}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                          v{doc.version}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          {doc.doc_type}
                        </span>
                      </div>
                      <h4 className="text-sm font-semibold text-slate-200 mt-1">{doc.title}</h4>
                      <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-1">
                        <span>{doc.page_count} Pages</span>
                        <span>•</span>
                        <span>{doc.is_scanned ? 'PaddleOCR Scanned' : 'PyMuPDF Native'}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <span className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Indexed</span>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

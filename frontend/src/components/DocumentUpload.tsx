'use client';

import React, { useState } from 'react';
import { Upload, FileCheck, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { DocumentUploadResponse } from '@/lib/types';

interface Props {
  onSuccess?: (res: DocumentUploadResponse) => void;
}

export default function DocumentUpload({ onSuccess }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [standardNumber, setStandardNumber] = useState('');
  const [title, setTitle] = useState('');
  const [version, setVersion] = useState('1.0');
  const [docType, setDocType] = useState('Standard');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<DocumentUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !standardNumber.trim()) {
      setError('Please select a file and specify a BIS standard number.');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.uploadDocument(file, standardNumber, title, version, docType);
      setResult(res);
      if (onSuccess) onSuccess(res);
      // Reset form
      setFile(null);
      setStandardNumber('');
      setTitle('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Document upload and processing failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleUpload} className="space-y-4">
      {/* File Dropzone */}
      <div className="border-2 border-dashed border-slate-700 hover:border-blue-500/60 rounded-2xl p-6 bg-slate-900/40 text-center transition">
        <label className="cursor-pointer flex flex-col items-center justify-center gap-2">
          <Upload className="w-8 h-8 text-blue-400" />
          <span className="text-sm font-semibold text-slate-200">
            {file ? file.name : 'Choose a BIS PDF or scanned document'}
          </span>
          <span className="text-xs text-slate-500">
            Supports official BIS PDFs, amendments, scanned standards (.pdf, .png, .jpg)
          </span>
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            className="hidden"
            onChange={(e) => {
              if (e.target.files?.[0]) setFile(e.target.files[0]);
            }}
          />
        </label>
      </div>

      {/* Metadata Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Standard Number *</label>
          <input
            type="text"
            required
            placeholder="e.g. IS 10500:2012"
            value={standardNumber}
            onChange={(e) => setStandardNumber(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Document Version</label>
          <input
            type="text"
            placeholder="e.g. 1.0 or 2018 Rev"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-xs font-medium text-slate-400 mb-1">Document Title</label>
          <input
            type="text"
            placeholder="e.g. Drinking Water — Specification"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-xs font-medium text-slate-400 mb-1">Document Type</label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option value="Standard">Indian Standard (IS)</option>
            <option value="Scheme">Certification Scheme (ISI/CRS)</option>
            <option value="Guideline">Regulatory Guideline</option>
            <option value="Laboratory">Laboratory Accreditation Manual</option>
            <option value="Update">Gazette Notification / Amendment</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs space-y-1">
          <div className="flex items-center gap-2 font-bold text-sm">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            <span>Ingestion Successful!</span>
          </div>
          <p>Document: {result.standard_number} (v{result.version})</p>
          <p>Pages Processed: {result.page_count} | Scanned OCR: {result.is_scanned ? 'Yes (PaddleOCR)' : 'No (PyMuPDF Text)'}</p>
          <p>Chunks Indexed: {result.chunks_created} in PostgreSQL, Elasticsearch, Qdrant & Neo4j.</p>
        </div>
      )}

      <button
        type="submit"
        disabled={uploading || !file || !standardNumber.trim()}
        className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white font-semibold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 transition"
      >
        {uploading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Processing via PyMuPDF / PaddleOCR & Indexing...</span>
          </>
        ) : (
          <span>Upload & Ingest to Knowledge Base</span>
        )}
      </button>
    </form>
  );
}

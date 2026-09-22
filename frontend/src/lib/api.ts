import axios from 'axios';
import { QueryResponse, DocumentUploadResponse, BISDocumentRecord, BISStandardSummary } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Query operations
  submitQuery: async (query: string, language: string = 'en'): Promise<QueryResponse> => {
    const response = await client.post<QueryResponse>('/api/query', { query, language });
    return response.data;
  },

  submitVoiceQuery: async (audioFile: File, language: string = 'en'): Promise<QueryResponse> => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('language', language);
    const response = await client.post<QueryResponse>('/api/query/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  submitDocumentQuery: async (docFile: File, query: string, language: string = 'en'): Promise<QueryResponse> => {
    const formData = new FormData();
    formData.append('document', docFile);
    formData.append('query', query);
    formData.append('language', language);
    const response = await client.post<QueryResponse>('/api/query/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Document management
  uploadDocument: async (
    file: File,
    standardNumber: string,
    title?: string,
    version: string = '1.0',
    docType: string = 'Standard'
  ): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('standard_number', standardNumber);
    if (title) formData.append('title', title);
    formData.append('version', version);
    formData.append('doc_type', docType);

    const response = await client.post<DocumentUploadResponse>('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocuments: async (): Promise<BISDocumentRecord[]> => {
    const response = await client.get<BISDocumentRecord[]>('/api/documents');
    return response.data;
  },

  getStandards: async (): Promise<BISStandardSummary[]> => {
    const response = await client.get<BISStandardSummary[]>('/api/standards');
    return response.data;
  },

  submitFeedback: async (queryId: number, feedback: string, comments?: string) => {
    const response = await client.post('/api/feedback', {
      query_id: queryId,
      feedback,
      comments,
    });
    return response.data;
  },
};

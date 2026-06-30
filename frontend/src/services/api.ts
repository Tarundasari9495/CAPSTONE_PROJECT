import axios from 'axios';
import type {
  AnalysisReport,
  ContractHistoryItem,
  ContractRecord,
  ContractUploadResponse,
} from '@/types/contract';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({ baseURL: BASE_URL });

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─────────────────────────────────────────────────────────────
// Auth
// ─────────────────────────────────────────────────────────────

export async function issueTestToken(userId?: string): Promise<string> {
  const { data } = await api.post<{ access_token: string }>('/auth/token', {
    user_id: userId ?? '00000000-0000-0000-0000-000000000001',
  });
  localStorage.setItem('access_token', data.access_token);
  return data.access_token;
}

export function logout(): void {
  localStorage.removeItem('access_token');
}

export function getToken(): string | null {
  return localStorage.getItem('access_token');
}

// ─────────────────────────────────────────────────────────────
// Contracts
// ─────────────────────────────────────────────────────────────

export async function uploadContract(file: File): Promise<ContractUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await api.post<ContractUploadResponse>('/contracts/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export function createAnalysisStream(contractId: string, file: File): EventSource {
  // SSE with file requires POST — we use fetch + ReadableStream instead
  // Return a wrapper that mimics EventSource API
  throw new Error(
    'Use analyzeContractWithStream for SSE POST. This method is not supported.',
  );
}

export async function* analyzeContractStream(
  contractId: string,
  file: File,
): AsyncGenerator<string> {
  const token = localStorage.getItem('access_token');
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/contracts/analyze/${contractId}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Analysis request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        yield line.slice(6);
      }
    }
  }
}

export async function getContract(contractId: string): Promise<ContractRecord> {
  const { data } = await api.get<ContractRecord>(`/contracts/${contractId}`);
  return data;
}

export async function getContractAnalysis(contractId: string): Promise<AnalysisReport> {
  const { data } = await api.get<AnalysisReport>(`/contracts/${contractId}/analysis`);
  return data;
}

export async function getContractHistory(): Promise<ContractHistoryItem[]> {
  const { data } = await api.get<ContractHistoryItem[]>('/contracts/history');
  return data;
}

export async function deleteContract(contractId: string): Promise<void> {
  await api.delete(`/contracts/${contractId}`);
}

export default api;

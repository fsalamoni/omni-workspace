/* ─────────────────────────────────────────────
   OmniWorkspace — REST API Client
   ───────────────────────────────────────────── */

import type { ApiKeyConfig, MCPServer, Session } from '@/types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/* ── helpers ─────────────────────────────── */

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;

  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(
      `API ${options.method ?? 'GET'} ${path} failed (${res.status}): ${body}`,
    );
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

/* ── Sessions ────────────────────────────── */

export async function createSession(title?: string): Promise<Session> {
  return request<Session>('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ title: title ?? 'New Session' }),
  });
}

export async function getSessions(): Promise<Session[]> {
  return request<Session[]>('/api/sessions');
}

export async function getSession(id: string): Promise<Session> {
  return request<Session>(`/api/sessions/${id}`);
}

export async function deleteSession(id: string): Promise<void> {
  return request<void>(`/api/sessions/${id}`, { method: 'DELETE' });
}

/* ── API Keys ────────────────────────────── */

export async function saveApiKeys(
  keys: ApiKeyConfig[],
): Promise<{ status: string }> {
  return request<{ status: string }>('/api/settings/api-keys', {
    method: 'POST',
    body: JSON.stringify({ keys }),
  });
}

export async function getApiKeys(): Promise<ApiKeyConfig[]> {
  return request<{ keys: ApiKeyConfig[] }>('/api/settings/api-keys').then(data => data.keys);
}

export async function getModels(): Promise<
  { provider: string; models: string[] }[]
> {
  return request<{ provider: string; models: string[] }[]>(
    '/api/settings/models',
  );
}

/* ── MCP Servers ─────────────────────────── */

export async function getMCPServers(): Promise<MCPServer[]> {
  return request<MCPServer[]>('/api/mcp/servers');
}

export async function addMCPServer(
  config: Omit<MCPServer, 'status' | 'tools'>,
): Promise<MCPServer> {
  return request<MCPServer>('/api/mcp/servers', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

export async function removeMCPServer(name: string): Promise<void> {
  return request<void>(`/api/mcp/servers/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  });
}

export async function getProviders(): Promise<string[]> {
  return request<{ providers: string[] }>('/api/providers').then((data) => data.providers);
}

export async function getGlobalModels(): Promise<any[]> {
  return request<{ models: any[] }>('/api/models/global').then((data) => data.models);
}

export async function getPersonalCatalog(): Promise<any[]> {
  return request<{ catalog: any[] }>('/api/settings/catalog').then((data) => data.catalog);
}

export async function savePersonalCatalog(catalog: any[]): Promise<void> {
  return request<void>('/api/settings/catalog', {
    method: 'POST',
    body: JSON.stringify(catalog),
  });
}

export async function getAgentConfigs(): Promise<Record<string, string>> {
  return request<{ configs: Record<string, string> }>('/api/settings/agents').then((data) => data.configs);
}

export async function saveAgentConfigs(configs: Record<string, string>): Promise<void> {
  return request<void>('/api/settings/agents', {
    method: 'POST',
    body: JSON.stringify(configs),
  });
}

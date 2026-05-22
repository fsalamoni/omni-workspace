/* ─────────────────────────────────────────────
   OmniWorkspace — Settings Store (Zustand + persist)
   ───────────────────────────────────────────── */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AgentInfo, ApiKeyConfig, MCPServer, PanelType } from '@/types';

interface SettingsState {
  /* persisted */
  apiKeys: ApiKeyConfig[];
  mcpServers: MCPServer[];
  theme: 'dark' | 'light';
  sidebarCollapsed: boolean;
  activePanel: PanelType;
  defaultModels: {
    planning: string;
    execution: string;
    vision: string;
  };

  /* runtime */
  agents: AgentInfo[];
  terminalLines: string[];

  /* actions */
  setApiKey: (provider: string, key: string, models?: string[]) => void;
  removeApiKey: (provider: string) => void;
  addMCPServer: (server: MCPServer) => void;
  removeMCPServer: (name: string) => void;
  updateMCPServerStatus: (name: string, status: MCPServer['status']) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setActivePanel: (panel: PanelType) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setDefaultModel: (role: 'planning' | 'execution' | 'vision', model: string) => void;
  setAgents: (agents: AgentInfo[]) => void;
  updateAgent: (agent: AgentInfo) => void;
  addTerminalLine: (line: string) => void;
  clearTerminal: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKeys: [],
      mcpServers: [],
      theme: 'dark',
      sidebarCollapsed: false,
      activePanel: 'chat',
      defaultModels: {
        planning: '',
        execution: '',
        vision: '',
      },
      agents: [],
      terminalLines: [],

      setApiKey: (provider, key, models) =>
        set((s) => {
          const existing = s.apiKeys.findIndex((k) => k.provider === provider);
          const updated = [...s.apiKeys];
          if (existing >= 0) {
            updated[existing] = { provider, key, models };
          } else {
            updated.push({ provider, key, models });
          }
          return { apiKeys: updated };
        }),

      removeApiKey: (provider) =>
        set((s) => ({
          apiKeys: s.apiKeys.filter((k) => k.provider !== provider),
        })),

      addMCPServer: (server) =>
        set((s) => ({ mcpServers: [...s.mcpServers, server] })),

      removeMCPServer: (name) =>
        set((s) => ({
          mcpServers: s.mcpServers.filter((srv) => srv.name !== name),
        })),

      updateMCPServerStatus: (name, status) =>
        set((s) => ({
          mcpServers: s.mcpServers.map((srv) =>
            srv.name === name ? { ...srv, status } : srv,
          ),
        })),

      toggleSidebar: () =>
        set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed) =>
        set({ sidebarCollapsed: collapsed }),

      setActivePanel: (panel) => set({ activePanel: panel }),

      setTheme: (theme) => set({ theme }),

      setDefaultModel: (role, model) =>
        set((s) => ({
          defaultModels: { ...s.defaultModels, [role]: model },
        })),

      setAgents: (agents) => set({ agents }),

      updateAgent: (agent) =>
        set((s) => {
          const idx = s.agents.findIndex((a) => a.id === agent.id);
          if (idx >= 0) {
            const updated = [...s.agents];
            updated[idx] = agent;
            return { agents: updated };
          }
          return { agents: [...s.agents, agent] };
        }),

      addTerminalLine: (line) =>
        set((s) => ({
          terminalLines: [...s.terminalLines, line].slice(-1000),
        })),

      clearTerminal: () => set({ terminalLines: [] }),
    }),
    {
      name: 'omni-workspace-settings',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        apiKeys: state.apiKeys,
        mcpServers: state.mcpServers,
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        activePanel: state.activePanel,
        defaultModels: state.defaultModels,
      }),
    },
  ),
);

/* ─────────────────────────────────────────────
   OmniWorkspace — Shared Type Definitions
   ───────────────────────────────────────────── */

export type EventType =
  | 'message'
  | 'action'
  | 'observation'
  | 'plan'
  | 'delegation'
  | 'error'
  | 'condensation';

export type AgentState = 'idle' | 'running' | 'finished' | 'error';

export type PlanStepStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface OmniEvent {
  id: string;
  timestamp: string;
  event_type: EventType;
  data: Record<string, unknown>;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  status: string;
  events: OmniEvent[];
}

export interface PlanStep {
  id: string;
  title: string;
  description: string;
  status: PlanStepStatus;
  agent_type?: string;
  result?: string;
}

export interface Plan {
  id: string;
  title: string;
  steps: PlanStep[];
  status: string;
}

export interface ApiKeyConfig {
  provider: string;
  key: string;
  models?: string[];
}

export interface MCPServer {
  name: string;
  description: string;
  command: string;
  args: string[];
  env: Record<string, string>;
  transport: 'stdio' | 'sse' | 'http';
  status: 'connected' | 'disconnected' | 'error';
  tools: string[];
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
  result?: string;
}

export interface FileAttachment {
  name: string;
  path: string;
  type: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: string;
  reasoning?: string;
  tool_calls?: ToolCall[];
  files?: FileAttachment[];
}

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  state: AgentState;
  current_step?: string;
  progress?: number;
}

export interface ModelInfo {
  id: string;
  label: string;
  provider: string;
  tier: string;
}

export interface CatalogEntry extends ModelInfo {}

export interface AgentConfig {
  [agentName: string]: string; // Maps agent name to model id
}

export type PanelType = 'chat' | 'cowork' | 'plan' | 'agents' | 'settings' | 'terminal' | 'catalog';

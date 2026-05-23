/* ─────────────────────────────────────────────
   SalomoneUI — Socket.IO Client
   ───────────────────────────────────────────── */

import { io, type Socket } from 'socket.io-client';
import type { AgentInfo, OmniEvent, Plan } from '@/types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

type EventCallback = (event: OmniEvent) => void;
type PlanCallback = (plan: Plan) => void;
type AgentCallback = (agent: AgentInfo) => void;
type ErrorCallback = (error: { message: string; code?: string }) => void;
type ConnectionCallback = (connected: boolean) => void;
type SandboxLogCallback = (log: any) => void;

class OmniSocket {
  private socket: Socket | null = null;

  private eventListeners: Set<EventCallback> = new Set();
  private planListeners: Set<PlanCallback> = new Set();
  private agentListeners: Set<AgentCallback> = new Set();
  private errorListeners: Set<ErrorCallback> = new Set();
  private connectionListeners: Set<ConnectionCallback> = new Set();
  private sandboxListeners: Set<SandboxLogCallback> = new Set();

  get connected(): boolean {
    return this.socket?.connected ?? false;
  }

  /* ── lifecycle ─────────────────────────── */

  connect(): void {
    if (this.socket?.connected) return;

    this.socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 10000,
      timeout: 20000,
    });

    this.socket.on('connect', () => {
      console.log('[OmniSocket] connected', this.socket?.id);
      this.notifyConnection(true);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[OmniSocket] disconnected:', reason);
      this.notifyConnection(false);
    });

    this.socket.on('connect_error', (err) => {
      console.warn('[OmniSocket] connection error:', err.message);
      this.notifyConnection(false);
    });

    /* ── server events ───────────────────── */

    this.socket.on('event', (data: OmniEvent) => {
      this.eventListeners.forEach((cb) => cb(data));
    });

    this.socket.on('plan_update', (data: Plan) => {
      this.planListeners.forEach((cb) => cb(data));
    });

    this.socket.on('agent_status', (data: AgentInfo) => {
      this.agentListeners.forEach((cb) => cb(data));
    });

    this.socket.on('error', (data: { message: string; code?: string }) => {
      this.errorListeners.forEach((cb) => cb(data));
    });

    this.socket.on('sandbox_event', (data: any) => {
      this.sandboxListeners.forEach((cb) => cb(data));
    });
  }

  disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
  }

  /* ── emitters ──────────────────────────── */

  sendMessage(sessionId: string, message: string): void {
    this.socket?.emit('user_message', { session_id: sessionId, message });
  }

  cancelAgent(sessionId: string): void {
    this.socket?.emit('cancel_agent', { session_id: sessionId });
  }

  joinSession(sessionId: string): void {
    this.socket?.emit('join_session', { session_id: sessionId });
  }

  leaveSession(sessionId: string): void {
    this.socket?.emit('leave_session', { session_id: sessionId });
  }

  /* ── subscriptions ─────────────────────── */

  onEvent(cb: EventCallback): () => void {
    this.eventListeners.add(cb);
    return () => this.eventListeners.delete(cb);
  }

  onPlanUpdate(cb: PlanCallback): () => void {
    this.planListeners.add(cb);
    return () => this.planListeners.delete(cb);
  }

  onAgentStatus(cb: AgentCallback): () => void {
    this.agentListeners.add(cb);
    return () => this.agentListeners.delete(cb);
  }

  onError(cb: ErrorCallback): () => void {
    this.errorListeners.add(cb);
    return () => this.errorListeners.delete(cb);
  }

  onConnection(cb: ConnectionCallback): () => void {
    this.connectionListeners.add(cb);
    return () => this.connectionListeners.delete(cb);
  }

  onSandboxEvent(cb: SandboxLogCallback): () => void {
    this.sandboxListeners.add(cb);
    return () => this.sandboxListeners.delete(cb);
  }

  /* ── internal ──────────────────────────── */

  private notifyConnection(connected: boolean): void {
    this.connectionListeners.forEach((cb) => cb(connected));
  }
}

export const omniSocket = new OmniSocket();

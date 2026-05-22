/* ─────────────────────────────────────────────
   OmniWorkspace — Session Store (Zustand)
   ───────────────────────────────────────────── */

import { create } from 'zustand';
import type { ChatMessage, Session } from '@/types';

interface SessionState {
  sessions: Session[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;

  /* actions */
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  removeSession: (id: string) => void;
  setActiveSession: (id: string | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, patch: Partial<ChatMessage>) => void;
  setStreaming: (streaming: boolean) => void;
  setStreamingContent: (content: string) => void;
  appendStreamingContent: (chunk: string) => void;
  clearMessages: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',

  setSessions: (sessions) => set({ sessions }),

  addSession: (session) =>
    set((s) => ({ sessions: [session, ...s.sessions] })),

  removeSession: (id) =>
    set((s) => ({
      sessions: s.sessions.filter((sess) => sess.id !== id),
      activeSessionId: s.activeSessionId === id ? null : s.activeSessionId,
    })),

  setActiveSession: (id) => set({ activeSessionId: id, messages: [] }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((s) => ({ messages: [...s.messages, message] })),

  updateMessage: (id, patch) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, ...patch } : m,
      ),
    })),

  setStreaming: (isStreaming) =>
    set({ isStreaming, streamingContent: isStreaming ? '' : '' }),

  setStreamingContent: (streamingContent) => set({ streamingContent }),

  appendStreamingContent: (chunk) =>
    set((s) => ({ streamingContent: s.streamingContent + chunk })),

  clearMessages: () => set({ messages: [] }),
}));

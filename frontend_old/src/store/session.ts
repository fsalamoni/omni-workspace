import { create } from 'zustand';
import { omniSocket } from '../services/socket';
import { OmniEvent, Session } from '../types';
import { createSession as createApiSession } from '../services/api';

export interface SandboxLog {
  type: string;
  command: string;
  stdout: string;
  stderr: string;
  exit_code: number;
}

interface SessionState {
  currentSessionId: string | null;
  events: OmniEvent[];
  sandboxLogs: SandboxLog[];
  connected: boolean;
  initializeSession: () => Promise<void>;
  sendMessage: (msg: string) => void;
  addEvent: (event: OmniEvent) => void;
  setConnected: (status: boolean) => void;
}

export const useSessionStore = create<SessionState>((set, get) => {
  // Setup socket listeners
  omniSocket.onConnection((status) => {
    set({ connected: status });
  });

  omniSocket.onEvent((event) => {
    set((state) => ({ events: [...state.events, event] }));
  });

  omniSocket.onSandboxEvent((log: SandboxLog) => {
    set((state) => ({ sandboxLogs: [...state.sandboxLogs, log] }));
  });

  omniSocket.connect();

  return {
    currentSessionId: null,
    events: [],
    sandboxLogs: [],
    connected: false,
    
    initializeSession: async () => {
      try {
        const session = await createApiSession('New Session');
        set({ currentSessionId: session.id, events: [] });
        omniSocket.joinSession(session.id);
      } catch (e) {
        console.error("Failed to create session:", e);
      }
    },

    sendMessage: (msg: string) => {
      const { currentSessionId } = get();
      if (currentSessionId) {
        omniSocket.sendMessage(currentSessionId, msg);
      }
    },

    addEvent: (event: OmniEvent) => {
      set((state) => ({ events: [...state.events, event] }));
    },
    
    setConnected: (status: boolean) => set({ connected: status })
  };
});

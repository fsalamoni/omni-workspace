/* ─────────────────────────────────────────────
   SalomoneUI — useSocket Hook
   ───────────────────────────────────────────── */

import { useCallback, useEffect, useRef, useState } from 'react';
import { omniSocket } from '@/services/socket';
import { useSessionStore } from '@/stores/sessionStore';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';
import type { ChatMessage } from '@/types';

export function useSocket() {
  const [connected, setConnected] = useState(omniSocket.connected);
  const initialized = useRef(false);

  const {
    activeSessionId,
    addMessage,
    setStreaming,
    appendStreamingContent,
    setStreamingContent,
  } = useSessionStore();

  const { setPlan } = usePlanStore();
  const { updateAgent, addTerminalLine } = useSettingsStore();

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    omniSocket.connect();

    const unsubs = [
      omniSocket.onConnection((c) => setConnected(c)),

      omniSocket.onEvent((event) => {
        switch (event.event_type) {
          case 'message': {
            const msg = event.data as unknown as ChatMessage;
            if (msg.role === 'assistant') {
              setStreaming(false);
              setStreamingContent('');
            }
            addMessage({
              id: event.id,
              role: (msg.role as ChatMessage['role']) ?? 'assistant',
              content: (msg.content as string) ?? '',
              timestamp: event.timestamp,
              reasoning: msg.reasoning,
              tool_calls: msg.tool_calls,
              files: msg.files,
            });
            break;
          }
          case 'action':
          case 'observation': {
            const content = (event.data.output as string) ?? (event.data.content as string) ?? '';
            if (content) addTerminalLine(content);
            break;
          }
          case 'error': {
            setStreaming(false);
            addMessage({
              id: event.id,
              role: 'system',
              content: `Error: ${event.data.message ?? 'Unknown error'}`,
              timestamp: event.timestamp,
            });
            break;
          }
          case 'condensation': {
            appendStreamingContent((event.data.chunk as string) ?? '');
            break;
          }
          default:
            break;
        }
      }),

      omniSocket.onPlanUpdate((plan) => {
        setPlan(plan);
      }),

      omniSocket.onAgentStatus((agent) => {
        updateAgent(agent);
      }),

      omniSocket.onError((err) => {
        console.error('[OmniSocket] error:', err);
      }),
    ];

    return () => {
      unsubs.forEach((unsub) => unsub());
      omniSocket.disconnect();
      initialized.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* Join / leave session when activeSessionId changes */
  const prevSession = useRef<string | null>(null);
  useEffect(() => {
    if (prevSession.current) {
      omniSocket.leaveSession(prevSession.current);
    }
    if (activeSessionId) {
      omniSocket.joinSession(activeSessionId);
    }
    prevSession.current = activeSessionId;
  }, [activeSessionId]);

  const sendMessage = useCallback(
    (message: string) => {
      if (!activeSessionId) return;
      setStreaming(true);
      omniSocket.sendMessage(activeSessionId, message);
    },
    [activeSessionId, setStreaming],
  );

  const cancelAgent = useCallback(() => {
    if (!activeSessionId) return;
    omniSocket.cancelAgent(activeSessionId);
    setStreaming(false);
  }, [activeSessionId, setStreaming]);

  return { connected, sendMessage, cancelAgent };
}

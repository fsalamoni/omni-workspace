import React, { useState } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { useSessionStore } from '../../store/session';
import { OmniEvent } from '../../types';

export default function ChatPanel() {
  const { events, sendMessage, connected } = useSessionStore();
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim() || !connected) return;
    sendMessage(input);
    setInput('');
  };

  // Filter events to only show user messages and final agent responses in chat
  // For now, we'll map MessageEvents
  const chatEvents = events.filter(e => e.event_type === 'message' || e.event_type === 'error');

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {chatEvents.map((msg, i) => {
          const isUser = msg.source === 'user';
          return (
            <div key={msg.id || i} style={{
              alignSelf: isUser ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              background: isUser ? 'var(--bg-elevated)' : 'var(--bg-glass)',
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              borderLeft: !isUser ? '3px solid var(--accent-purple)' : '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontWeight: 600, marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                {isUser ? 'You' : msg.source}
              </div>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
            </div>
          );
        })}
      </div>
      
      <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-secondary)' }}>
        <div className="glass" style={{ display: 'flex', alignItems: 'flex-end', padding: '12px', borderRadius: 'var(--radius-lg)', gap: '12px' }}>
          <button className="btn btn-ghost" style={{ padding: '8px' }}>
            <Paperclip size={20} />
          </button>
          <textarea
            className="input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask SalomoneUI to build something..."
            style={{ 
              flex: 1, 
              background: 'transparent', 
              border: 'none', 
              resize: 'none', 
              height: '40px', 
              maxHeight: '200px',
              padding: '8px 0',
              boxShadow: 'none'
            }}
          />
          <button className="btn btn-primary" onClick={handleSend} style={{ padding: '8px' }}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

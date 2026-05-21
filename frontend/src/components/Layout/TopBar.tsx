import React from 'react';
import { Play } from 'lucide-react';

export default function TopBar() {
  return (
    <div style={{ 
      height: '60px', 
      borderBottom: '1px solid var(--border-subtle)', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      padding: '0 24px',
      background: 'var(--bg-primary)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>New Session</div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          <span className="status-dot idle"></span>
          Backend Disconnected
        </div>
        <button className="btn btn-primary">
          <Play size={16} /> Run Agent
        </button>
      </div>
    </div>
  );
}

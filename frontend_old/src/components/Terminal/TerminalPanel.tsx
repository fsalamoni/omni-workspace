import React from 'react';
import { useSessionStore } from '../../store/session';

export default function TerminalPanel() {
  const { sandboxLogs } = useSessionStore();

  return (
    <div style={{ flex: 1, backgroundColor: '#000', color: '#00ff00', fontFamily: '"JetBrains Mono", monospace', padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #333', paddingBottom: '8px', marginBottom: '16px' }}>
        <span style={{ color: '#fff', fontSize: '0.875rem' }}>Sandbox Terminal</span>
        <span style={{ color: '#666', fontSize: '0.75rem' }}>Read-only (Live Execution Logs)</span>
      </div>
      <div style={{ flex: 1 }}>
        <div>$ docker exec -it workspace_1 bash</div>
        <div>Workspace initialized.</div>
        <div style={{ color: '#aaa', marginBottom: '16px' }}>Waiting for commands...</div>
        
        {sandboxLogs.map((log, i) => (
          <div key={i} style={{ marginBottom: '12px' }}>
            <div style={{ color: '#00ffff' }}>$ {log.command}</div>
            {log.stdout && <div style={{ color: '#ccc', whiteSpace: 'pre-wrap' }}>{log.stdout}</div>}
            {log.stderr && <div style={{ color: '#ff5555', whiteSpace: 'pre-wrap' }}>{log.stderr}</div>}
            {log.exit_code !== 0 && (
              <div style={{ color: '#ff5555' }}>[Exited with code {log.exit_code}]</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

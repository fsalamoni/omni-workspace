import React, { useState } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import ChatPanel from '../Chat/ChatPanel';
import CoworkPanel from '../Cowork/CoworkPanel';
import PlanVisualizer from '../PlanView/PlanVisualizer';
import SettingsPanel from '../Settings/SettingsPanel';
import CatalogPanel from '../Settings/CatalogPanel';
import AgentDashboard from '../AgentPanel/AgentDashboard';
import TerminalPanel from '../Terminal/TerminalPanel';
import { PanelType } from '../../types';

export default function Shell() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activePanel, setActivePanel] = useState<PanelType>('chat');

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
        activePanel={activePanel}
        onSelectPanel={setActivePanel}
      />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopBar />
        <main style={{ flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
          {activePanel === 'chat' && (
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
              <div style={{ flex: '0 0 50%', borderRight: '1px solid var(--border-subtle)' }}>
                <ChatPanel />
              </div>
              <div style={{ flex: '0 0 50%' }}>
                <CoworkPanel />
              </div>
            </div>
          )}

          {activePanel === 'plan' && (
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
              <PlanVisualizer />
            </div>
          )}
          
          {activePanel === 'settings' && <SettingsPanel />}
          {activePanel === 'catalog' && <CatalogPanel />}
          {activePanel === 'agents' && <AgentDashboard />}
          {activePanel === 'terminal' && <TerminalPanel />}
        </main>
      </div>
    </div>
  );
}

import React from 'react';
import { MessageSquare, Settings, PanelLeftClose, PanelLeftOpen, Code2, Users, GitBranch, Terminal, Library } from 'lucide-react';
import { PanelType } from '../../types';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  activePanel: PanelType;
  onSelectPanel: (panel: PanelType) => void;
}

export default function Sidebar({ collapsed, onToggle, activePanel, onSelectPanel }: SidebarProps) {
  const width = collapsed ? '60px' : '240px';
  
  const NavItem = ({ icon: Icon, label, id }: { icon: any, label: string, id: PanelType }) => {
    const isActive = activePanel === id;
    return (
      <button 
        onClick={() => onSelectPanel(id)}
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          width: '100%', 
          padding: '12px 16px', 
          background: isActive ? 'var(--bg-elevated)' : 'transparent',
          border: 'none',
          borderLeft: isActive ? '3px solid var(--accent-cyan)' : '3px solid transparent',
          color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
          cursor: 'pointer',
          textAlign: 'left',
          transition: 'all 0.2s',
        }}
        className="glass-hover"
      >
        <Icon size={20} style={{ minWidth: '20px' }} color={isActive ? 'var(--accent-cyan)' : 'currentColor'} />
        {!collapsed && <span style={{ marginLeft: '12px', fontWeight: 500 }}>{label}</span>}
      </button>
    );
  };

  return (
    <div style={{ 
      width, 
      height: '100%', 
      background: 'var(--bg-secondary)', 
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      transition: 'width 0.2s ease'
    }}>
      <div style={{ padding: '20px 16px', display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'space-between' }}>
        {!collapsed && <div style={{ fontWeight: 700, fontSize: '1.25rem' }} className="gradient-text">SalomoneUI</div>}
        <button onClick={onToggle} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
          {collapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>
      
      <div style={{ flex: 1, marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <NavItem icon={MessageSquare} label="Chat & Execute" id="chat" />
        <NavItem icon={GitBranch} label="Execution Plan" id="plan" />
        <NavItem icon={Users} label="Agent Team" id="agents" />
        <NavItem icon={Library} label="Personal Catalog" id="catalog" />
        <NavItem icon={Terminal} label="Sandbox Terminal" id="terminal" />
        <NavItem icon={Settings} label="Settings" id="settings" />
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { AgentInfo, CatalogEntry } from '../../types';
import { getPersonalCatalog, getAgentConfigs, saveAgentConfigs } from '../../services/api';

// Mock data for initial UI dev
const MOCK_AGENTS: AgentInfo[] = [
  { id: '1', name: 'Manus', role: 'General Purpose Exec Agent', state: 'idle' },
  { id: '2', name: 'Browser', role: 'Playwright Browser Agent', state: 'idle' },
  { id: '3', name: 'Desktop', role: 'Computer Control VLM', state: 'idle' },
];

export default function AgentDashboard() {
  const [catalog, setCatalog] = useState<CatalogEntry[]>([]);
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [cat, conf] = await Promise.all([
          getPersonalCatalog(),
          getAgentConfigs()
        ]);
        setCatalog(cat || []);
        setConfigs(conf || {});
      } catch (err) {
        console.error("Failed to load agent dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleModelSelect = async (agentName: string, modelId: string) => {
    const newConfigs = { ...configs, [agentName]: modelId };
    setConfigs(newConfigs);
    try {
      await saveAgentConfigs(newConfigs);
    } catch (err) {
      console.error("Failed to save config:", err);
    }
  };

  if (loading) return <div style={{ padding: 24 }}>Loading agents...</div>;

  return (
    <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
      <h2 style={{ marginBottom: '8px' }}>Agent Team Configuration</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
        Assign a model from your personal catalog to each specialized agent.
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '16px' }}>
        {MOCK_AGENTS.map((agent) => (
          <div key={agent.id} className="glass" style={{ padding: '20px', borderRadius: 'var(--radius-md)', position: 'relative', overflow: 'hidden' }}>
            {agent.state === 'running' && (
              <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '3px', background: 'linear-gradient(90deg, transparent, var(--accent-blue), transparent)', animation: 'scan 2s infinite linear' }} />
            )}
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.2rem' }}>{agent.name}</h3>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '4px' }}>{agent.role}</div>
              </div>
            </div>
            
            <div style={{ marginTop: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>
                Assigned Model
              </label>
              <select 
                className="input" 
                value={configs[agent.name] || ''} 
                onChange={(e) => handleModelSelect(agent.name, e.target.value)}
                style={{ width: '100%', backgroundColor: 'rgba(0,0,0,0.3)' }}
              >
                <option value="">-- Default / Not Set --</option>
                {catalog.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.id} ({model.provider})
                  </option>
                ))}
              </select>
            </div>
          </div>
        ))}
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes scan {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}} />
    </div>
  );
}

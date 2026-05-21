import React, { useState, useEffect } from 'react';
import { getApiKeys, saveApiKeys, getProviders } from '../../services/api';
import { ApiKeyConfig } from '../../types';

export default function SettingsPanel() {
  const [keys, setKeys] = useState<{ [provider: string]: string }>({});
  const [configured, setConfigured] = useState<{ [provider: string]: boolean }>({});
  const [providers, setProviders] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const provs = await getProviders();
        setProviders(provs);
        
        const storedKeys = await getApiKeys();
        const initialKeys: { [p: string]: string } = {};
        const confProvs: Record<string, boolean> = {};
        provs.forEach(p => {
          initialKeys[p] = '';
          confProvs[p] = false;
        });
        
        if (storedKeys && storedKeys.length > 0) {
          storedKeys.forEach(k => {
            initialKeys[k.provider] = k.key;
            if (k.key && k.key.trim() !== '') {
               confProvs[k.provider] = true;
            }
          });
        }
        setKeys(initialKeys);
        setConfigured(confProvs);
      } catch (err) {
        console.error("Failed to load data:", err);
      }
    }
    loadData();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    setMessage('');
    try {
      const config: ApiKeyConfig[] = Object.entries(keys)
        .map(([provider, key]) => ({ provider, key }));
        
      await saveApiKeys(config);
      setMessage('Keys saved successfully!');
      
      // Update configured visual state
      const confProvs = { ...configured };
      config.forEach(c => {
         if (c.key === '') confProvs[c.provider] = false;
         else if (!c.key.includes('***')) confProvs[c.provider] = true;
      });
      setConfigured(confProvs);
      
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
      <h2 style={{ marginBottom: '24px' }}>Settings</h2>
      
      <div className="glass" style={{ padding: '24px', borderRadius: 'var(--radius-md)' }}>
        <h3 style={{ marginBottom: '8px' }}>API Keys</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '0.875rem' }}>
          Configure your LLM provider keys here. These are stored securely in your local environment.
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '600px' }}>
          {providers.map((provider) => (
            <div key={provider}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.875rem', fontWeight: 500 }}>
                {provider} API Key {configured[provider] && <span style={{color: '#52c41a', marginLeft: '8px'}}>✓ Active</span>}
              </label>
              <input 
                type="password" 
                placeholder={configured[provider] ? `•••••••••••••••• (Active)` : `Enter ${provider} key...`} 
                className="input" 
                value={keys[provider] || ''}
                onChange={(e) => setKeys({ ...keys, [provider]: e.target.value })}
              />
            </div>
          ))}
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '12px' }}>
            <button 
              className="btn btn-primary" 
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Keys'}
            </button>
            {message && (
              <span style={{ fontSize: '0.875rem', color: message.startsWith('Error') ? '#ff4d4f' : '#52c41a' }}>
                {message}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

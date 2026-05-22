import React, { useState, useEffect, useMemo } from 'react';
import { getGlobalModels, getPersonalCatalog, savePersonalCatalog } from '../../services/api';
import { ModelInfo, CatalogEntry } from '../../types';

export default function CatalogPanel() {
  const [globalModels, setGlobalModels] = useState<ModelInfo[]>([]);
  const [personalCatalog, setPersonalCatalog] = useState<CatalogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProvider, setFilterProvider] = useState<string>('All');
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [models, catalog] = await Promise.all([
          getGlobalModels(),
          getPersonalCatalog()
        ]);
        setGlobalModels(models);
        setPersonalCatalog(catalog || []);
      } catch (err) {
        console.error("Failed to load models:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const providers = useMemo(() => {
    const provs = new Set<string>();
    globalModels.forEach(m => provs.add(m.provider));
    return ['All', ...Array.from(provs).sort()];
  }, [globalModels]);

  const filteredModels = useMemo(() => {
    return globalModels.filter(m => {
      const matchSearch = m.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchProv = filterProvider === 'All' || m.provider === filterProvider;
      return matchSearch && matchProv;
    });
  }, [globalModels, searchTerm, filterProvider]);

  const isInCatalog = (modelId: string) => personalCatalog.some(m => m.id === modelId);

  const toggleCatalog = async (model: ModelInfo) => {
    let newCatalog;
    if (isInCatalog(model.id)) {
      newCatalog = personalCatalog.filter(m => m.id !== model.id);
    } else {
      newCatalog = [...personalCatalog, model];
    }
    setPersonalCatalog(newCatalog);
    
    try {
      await savePersonalCatalog(newCatalog);
    } catch (err) {
      console.error("Failed to auto-save catalog:", err);
    }
  };

  const handleSave = async () => {
    try {
      setMessage('Saving...');
      await savePersonalCatalog(personalCatalog);
      setMessage('Catalog saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    }
  };

  if (loading) return <div style={{ padding: 24 }}>Loading catalog...</div>;

  return (
    <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', gap: '24px' }}>
      {/* Left: Global Models */}
      <div style={{ flex: 2, display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ marginBottom: '16px' }}>Global Models ({filteredModels.length})</h2>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input 
            type="text" 
            placeholder="Search models..." 
            className="input" 
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            style={{ flex: 1 }}
          />
          <select 
            className="input" 
            value={filterProvider} 
            onChange={e => setFilterProvider(e.target.value)}
            style={{ width: '200px' }}
          >
            {providers.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        
        <div className="glass" style={{ flex: 1, borderRadius: 'var(--radius-md)', overflowY: 'auto', maxHeight: 'calc(100vh - 180px)' }}>
          {filteredModels.map(model => (
            <div key={model.id} style={{ 
              padding: '12px 16px', 
              borderBottom: '1px solid rgba(255,255,255,0.05)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: 500 }}>{model.id}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{model.provider}</div>
              </div>
              <button 
                className={`btn ${isInCatalog(model.id) ? 'btn-secondary' : 'btn-primary'}`}
                style={{ padding: '4px 12px', fontSize: '0.8rem' }}
                onClick={() => toggleCatalog(model)}
              >
                {isInCatalog(model.id) ? 'Remove' : 'Add to Catalog'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Personal Catalog */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0 }}>My Catalog ({personalCatalog.length})</h2>
          <button className="btn btn-primary" onClick={handleSave}>Save Catalog</button>
        </div>
        {message && <div style={{ marginBottom: '12px', color: '#52c41a', fontSize: '0.9rem' }}>{message}</div>}
        
        <div className="glass" style={{ flex: 1, borderRadius: 'var(--radius-md)', padding: '16px', overflowY: 'auto', maxHeight: 'calc(100vh - 180px)' }}>
          {personalCatalog.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '40px' }}>
              Your catalog is empty. Add models from the global list.
            </div>
          ) : (
            personalCatalog.map(model => (
              <div key={model.id} style={{ 
                padding: '12px', 
                backgroundColor: 'rgba(0,0,0,0.2)', 
                borderRadius: 'var(--radius-sm)',
                marginBottom: '8px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>{model.id}</div>
                </div>
                <button 
                  style={{ background: 'none', border: 'none', color: '#ff4d4f', cursor: 'pointer', fontSize: '1.2rem' }}
                  onClick={() => toggleCatalog(model)}
                  title="Remove"
                >
                  &times;
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

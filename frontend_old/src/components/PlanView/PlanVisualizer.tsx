import React from 'react';
import ReactFlow, { Background, Controls, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 250, y: 5 }, data: { label: 'Analyze Request' }, type: 'input' },
  { id: '2', position: { x: 100, y: 100 }, data: { label: 'Create Backend' } },
  { id: '3', position: { x: 400, y: 100 }, data: { label: 'Create Frontend' } },
  { id: '4', position: { x: 250, y: 200 }, data: { label: 'Test System' }, type: 'output' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e1-3', source: '1', target: '3', animated: true },
  { id: 'e2-4', source: '2', target: '4' },
  { id: 'e3-4', source: '3', target: '4' },
];

export default function PlanVisualizer() {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--bg-secondary)', borderLeft: '1px solid var(--border-subtle)' }}>
      <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-primary)' }}>
        <h3 style={{ margin: 0, fontSize: '1rem' }}>Execution Plan</h3>
        <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Goal-Oriented Action Graph</p>
      </div>
      
      <div style={{ flex: 1, width: '100%' }}>
        <ReactFlow 
          nodes={initialNodes} 
          edges={initialEdges}
          fitView
          proOptions={{ hideAttribution: true }}
        >
          <Background color="var(--border-subtle)" gap={16} />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}

import React, { useEffect } from 'react';
import Shell from './components/Layout/Shell';
import { useSessionStore } from './store/session';

function App() {
  const initializeSession = useSessionStore(state => state.initializeSession);
  
  useEffect(() => {
    initializeSession();
  }, [initializeSession]);

  return (
    <Shell />
  );
}

export default App;

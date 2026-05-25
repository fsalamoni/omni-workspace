import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated';

export interface AuthUser {
  id: string;
  username: string;
  email?: string;
  photoURL?: string;
  isAdmin?: boolean;
}

interface LoginParams {
  username?: string; // used as email
  password?: string;
  remember?: boolean;
  provider?: 'google' | 'email';
}

type LoginErrorCode =
  | 'invalidCredentials'
  | 'tooManyAttempts'
  | 'serverError'
  | 'networkError'
  | 'unknown';

interface LoginResult {
  success: boolean;
  message?: string;
  code?: LoginErrorCode;
  shouldClearCache?: boolean;
}

interface AuthContextValue {
  ready: boolean;
  user: AuthUser | null;
  status: AuthStatus;
  login: (params: LoginParams) => Promise<LoginResult>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  clearAuthCache: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState<AuthStatus>('checking');
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Offline/Desktop mode: Bypass Firebase and authenticate directly
    setUser({
      id: 'local-admin',
      username: 'Salomone Local Admin',
      email: 'fsalamoni@gmail.com',
      isAdmin: true
    });
    setStatus('authenticated');
    setReady(true);
  }, []);

  const refresh = useCallback(async () => {
    // No-op for local
  }, []);

  const clearAuthCache = useCallback(() => {
    // No-op for local
  }, []);

  const login = useCallback(async ({ username, password }: LoginParams): Promise<LoginResult> => {
    setReady(true);
    return { success: true };
  }, []);

  const logout = useCallback(async () => {
    return;
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      ready,
      user,
      status,
      login,
      logout,
      refresh,
      clearAuthCache,
    }),
    [login, logout, ready, refresh, status, user, clearAuthCache]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

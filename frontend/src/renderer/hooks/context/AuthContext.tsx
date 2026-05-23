import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { auth } from '@/common/firebase';
import { 
  signInWithEmailAndPassword, 
  signInWithPopup, 
  GoogleAuthProvider, 
  signOut,
  onAuthStateChanged,
  User
} from 'firebase/auth';

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
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser: User | null) => {
      if (firebaseUser) {
        setUser({
          id: firebaseUser.uid,
          username: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'User',
          email: firebaseUser.email || undefined,
          photoURL: firebaseUser.photoURL || undefined,
          isAdmin: firebaseUser.email === 'fsalamoni@gmail.com'
        });
        setStatus('authenticated');
      } else {
        setUser(null);
        setStatus('unauthenticated');
      }
      setReady(true);
    });

    return () => unsubscribe();
  }, []);

  const refresh = useCallback(async () => {
    // onAuthStateChanged handles automatic refreshes
  }, []);

  const clearAuthCache = useCallback(() => {
    // No-op for Firebase Auth
  }, []);

  const login = useCallback(async ({ username, password, provider = 'email' }: LoginParams): Promise<LoginResult> => {
    try {
      if (provider === 'google') {
        const googleProvider = new GoogleAuthProvider();
        await signInWithPopup(auth, googleProvider);
      } else {
        if (!username || !password) {
          return { success: false, code: 'invalidCredentials', message: 'Email and password are required' };
        }
        await signInWithEmailAndPassword(auth, username, password);
      }
      
      return { success: true };
    } catch (error: any) {
      console.error('Firebase login error:', error);
      let code: LoginErrorCode = 'unknown';
      if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password' || error.code === 'auth/invalid-credential') {
        code = 'invalidCredentials';
      } else if (error.code === 'auth/too-many-requests') {
        code = 'tooManyAttempts';
      } else if (error.code === 'auth/network-request-failed') {
        code = 'networkError';
      }
      
      return {
        success: false,
        message: error.message || 'Login failed',
        code,
      };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await signOut(auth);
      setUser(null);
      setStatus('unauthenticated');
    } catch (error) {
      console.error('Logout request failed:', error);
    }
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

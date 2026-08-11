import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { fetchApi, getAccessToken, setTokens, clearTokens, loginOperator } from '../api';

interface Operator {
  id: string;
  name: string;
  email: string;
  phone: string;
  created_at: string;
}

interface AuthContextType {
  operator: Operator | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [operator, setOperator] = useState<Operator | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken();
      if (token) {
        try {
          const user = await fetchApi<Operator>('/auth/operator/me');
          setOperator(user);
        } catch {
          clearTokens();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const data = await loginOperator(email, password);
    setTokens(data.access_token, data.refresh_token);
    const user = await fetchApi<Operator>('/auth/operator/me');
    setOperator(user);
  };

  const logout = () => {
    clearTokens();
    setOperator(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ operator, loading, login, logout, isAuthenticated: !!operator }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
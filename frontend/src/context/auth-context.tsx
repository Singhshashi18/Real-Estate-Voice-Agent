"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import { api, type User } from "@/lib/api";

const TOKEN_KEY = "inbound_agent_token";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  completeOAuth: (accessToken: string, user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const persistSession = useCallback((accessToken: string, nextUser: User) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    setToken(accessToken);
    setUser(nextUser);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    router.push("/login");
  }, [router]);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await api.login(email, password);
      persistSession(data.access_token, data.user);
      router.push("/inbound");
    },
    [persistSession, router],
  );

  const register = useCallback(
    async (name: string, email: string, password: string) => {
      const data = await api.register(name, email, password);
      persistSession(data.access_token, data.user);
      router.push("/inbound");
    },
    [persistSession, router],
  );

  const completeOAuth = useCallback(
    (accessToken: string, nextUser: User) => {
      persistSession(accessToken, nextUser);
      router.push("/inbound");
    },
    [persistSession, router],
  );

  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setLoading(false);
      return;
    }

    api
      .me(stored)
      .then((me) => {
        setToken(stored);
        setUser(me);
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
      })
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo(
    () => ({ user, token, loading, login, register, completeOAuth, logout }),
    [user, token, loading, login, register, completeOAuth, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

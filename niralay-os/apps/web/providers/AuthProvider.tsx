"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { authApi, tokenStorage, CurrentUser } from "@/services/api";

interface AuthContextType {
  user: CurrentUser | null;
  isLoading: boolean;
  login: (tokenData: any) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  login: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const accessToken = tokenStorage.getAccess();
      if (!accessToken) {
        setIsLoading(false);
        return;
      }

      try {
        const cachedUser = tokenStorage.getUser();
        if (cachedUser) setUser(cachedUser);

        const res = await authApi.me();
        setUser(res.data);
        tokenStorage.setUser(res.data);
      } catch (err) {
        tokenStorage.clear();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    loadUser();
  }, []);

  const login = async (tokenData: any) => {
    tokenStorage.set(tokenData.access_token, tokenData.refresh_token);
    try {
      const res = await authApi.me();
      setUser(res.data);
      tokenStorage.setUser(res.data);
    } catch (err) {
      console.error("Failed to load profile after login", err);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (err) {
      // Ignore network errors on logout
    }
    tokenStorage.clear();
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

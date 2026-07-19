import {
  createContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";
import { apiClient, ApiError } from "@/lib/api-client";
import { AUTH_TOKEN_KEY } from "@/lib/storage";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/types/api";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (payload: LoginRequest) => Promise<void>;
  register: (payload: RegisterRequest) => Promise<void>;
  logout: () => void;
  getToken: () => string | null;
  getUser: () => User | null;
  refreshProfile: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    () => window.localStorage.getItem(AUTH_TOKEN_KEY),
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      const existingToken = window.localStorage.getItem(AUTH_TOKEN_KEY);
      if (!existingToken) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.get<User>("/auth/me");
        setToken(existingToken);
        setUser(response.data);
      } catch {
        window.localStorage.removeItem(AUTH_TOKEN_KEY);
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  async function login(payload: LoginRequest) {
    const response = await apiClient.post<TokenResponse>("/auth/login", payload);
    window.localStorage.setItem(AUTH_TOKEN_KEY, response.data.access_token);
    setToken(response.data.access_token);
    setUser(response.data.user);
  }

  async function register(payload: RegisterRequest) {
    await apiClient.post<User>("/auth/register", payload);
    await login({ email: payload.email, password: payload.password });
  }

  function logout() {
    window.localStorage.removeItem(AUTH_TOKEN_KEY);
    setToken(null);
    setUser(null);
  }

  function getToken(): string | null {
    return token;
  }

  function getUser(): User | null {
    return user;
  }

  async function refreshProfile() {
    if (!window.localStorage.getItem(AUTH_TOKEN_KEY)) {
      throw new ApiError("You are not signed in.", {
        status: 401,
        code: "http_error",
      });
    }

    const response = await apiClient.get<User>("/auth/me");
    setUser(response.data);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      loading,
      login,
      register,
      logout,
      getToken,
      getUser,
      refreshProfile,
    }),
    [loading, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
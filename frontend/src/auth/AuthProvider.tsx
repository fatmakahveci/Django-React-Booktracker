import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  api,
  ApiError,
  errorMessage,
  logout as endSession,
} from "../api/client";
import type { User } from "../types";
interface Auth {
  user: User | null;
  loading: boolean;
  error: string;
  reload: () => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  setUser: (user: User | null) => void;
}
const Context = createContext<Auth | null>(null);
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  async function reload() {
    setLoading(true);
    setError("");
    try {
      setUser(await api<User>("auth/me/"));
    } catch (e) {
      if (e instanceof ApiError && [400, 401, 403].includes(e.status))
        setUser(null);
      else setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void reload();
    const expire = () => setUser(null);
    window.addEventListener("session-expired", expire);
    return () => window.removeEventListener("session-expired", expire);
  }, []);
  const signIn = async (email: string, password: string) => {
    const result = await api<{ user: User }>(
      "auth/login/",
      "POST",
      { email, password },
      false,
    );
    setError("");
    setUser(result.user);
  };
  const signOut = async () => {
    await endSession();
    setUser(null);
  };
  return (
    <Context.Provider
      value={{ user, loading, error, reload, signIn, signOut, setUser }}
    >
      {children}
    </Context.Provider>
  );
}
export function useAuth() {
  const auth = useContext(Context);
  if (!auth) throw new Error("Missing AuthProvider");
  return auth;
}

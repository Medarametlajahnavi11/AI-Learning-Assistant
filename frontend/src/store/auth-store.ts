import { create } from "zustand";
import { clearAuthTokens, getAccessToken, getRefreshToken, setAuthTokens } from "@/lib/auth";

type UserProfile = {
  user_id: string;
  full_name: string;
  learning_level: string;
  preferred_explanation_style: string;
  preferred_learning_mode: string;
  subjects: string[];
  xp_points: number;
  learning_streak: number;
  daily_goal: number;
};

type AuthState = {
  token: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  setToken: (token: string | null, refreshToken: string | null) => void;
  setUser: (user: UserProfile | null) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: getAccessToken(),
  refreshToken: getRefreshToken(),
  user: null,
  setToken: (token, refreshToken) => {
    setAuthTokens(token, refreshToken);
    set({ token, refreshToken });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    clearAuthTokens();
    set({ token: null, refreshToken: null, user: null });
  },
}));

import { create } from "zustand";

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
  user: UserProfile | null;
  setToken: (token: string | null) => void;
  setUser: (user: UserProfile | null) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("access_token"),
  user: null,
  setToken: (token) => {
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
    set({ token });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem("access_token");
    set({ token: null, user: null });
  },
}));

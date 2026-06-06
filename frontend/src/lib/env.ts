export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL as string,
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL as string,
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY as string,
  appName: (import.meta.env.VITE_APP_NAME as string) || "AI Learning Assistant",
};

import axios, { AxiosError } from "axios";
import { env } from "@/lib/env";
import { clearAuthTokens, getAccessToken, getRefreshToken, redirectToLogin, setAuthTokens } from "@/lib/auth";

export const api = axios.create({
  baseURL: env.apiBaseUrl,
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    if (!originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401) {
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        originalRequest._retry = true;
        try {
          const refreshResponse = await axios.post(`${env.apiBaseUrl}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = refreshResponse.data;
          setAuthTokens(access_token, refresh_token);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          } else {
            originalRequest.headers = { Authorization: `Bearer ${access_token}` };
          }

          return api(originalRequest);
        } catch {
          redirectToLogin();
          return Promise.reject(error);
        }
      }

      redirectToLogin();
    }

    return Promise.reject(error);
  }
);

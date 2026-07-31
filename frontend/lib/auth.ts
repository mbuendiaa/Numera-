"use client";

const ACCESS_TOKEN = "numera_access_token";
const REFRESH_TOKEN = "numera_refresh_token";

export function getAccessToken() {
  return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_TOKEN);
}

export function getRefreshToken() {
  return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_TOKEN);
}

export function saveTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN, accessToken);
  localStorage.setItem(REFRESH_TOKEN, refreshToken);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(REFRESH_TOKEN);
}

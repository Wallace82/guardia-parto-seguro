import { Injectable } from '@angular/core';

const STORAGE_KEYS = {
  ACCESS_TOKEN:  'guardia_access_token',
  REFRESH_TOKEN: 'guardia_refresh_token',
  USER:          'guardia_user',
} as const;

/**
 * StorageService — wrapper seguro para localStorage.
 * Centraliza todas as operações de persistência de tokens JWT e perfil do usuário.
 */
@Injectable({ providedIn: 'root' })
export class StorageService {
  // ---- Access Token ----
  getAccessToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }

  setAccessToken(token: string): void {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
  }

  // ---- Refresh Token ----
  getRefreshToken(): string | null {
    return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
  }

  setRefreshToken(token: string): void {
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, token);
  }

  // ---- User Profile ----
  getUser<T>(): T | null {
    const raw = localStorage.getItem(STORAGE_KEYS.USER);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  }

  setUser(user: unknown): void {
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  }

  // ---- Limpar tudo (logout) ----
  clearAll(): void {
    Object.values(STORAGE_KEYS).forEach((key) =>
      localStorage.removeItem(key),
    );
  }

  // ---- Helpers ----
  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

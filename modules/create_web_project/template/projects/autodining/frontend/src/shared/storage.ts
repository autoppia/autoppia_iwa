export const isBrowser = (): boolean => typeof window !== "undefined";

export function readJson<T>(key: string, defaultValue: T | null = null): T | null {
  if (!isBrowser()) return defaultValue;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return defaultValue;
    return JSON.parse(raw) as T;
  } catch {
    return defaultValue;
  }
}

export function writeJson<T>(key: string, value: T): void {
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore
  }
}

export function readString(key: string, defaultValue: string | null = null): string | null {
  if (!isBrowser()) return defaultValue;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ?? defaultValue;
  } catch {
    return defaultValue;
  }
}

export function writeString(key: string, value: string): void {
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // ignore
  }
}



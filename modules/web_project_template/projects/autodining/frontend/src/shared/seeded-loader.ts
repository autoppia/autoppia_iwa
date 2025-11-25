import { getApiBaseUrl } from "./data-generator";

export interface SeededLoadOptions {
  projectKey: string;
  entityType: string;
  seedValue?: number;
  limit?: number;
  method?: "select" | "shuffle" | "filter" | "distribute";
  filterKey?: string;
  filterValues?: string[];
}

export function isDbLoadModeEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_ENABLE_DB_MODE || process.env.ENABLE_DB_MODE || "").toString().toLowerCase();
  return raw === "true";
}

export function getSeedValueFromEnv(defaultSeed: number = 1): number {
  const raw = (process.env.NEXT_PUBLIC_DATA_SEED_VALUE || process.env.DATA_SEED_VALUE || "").toString();
  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed <= 0) return defaultSeed;
  return Math.floor(parsed);
}

export async function fetchSeededSelection<T = any>(options: SeededLoadOptions): Promise<T[]> {
  const baseUrl = getApiBaseUrl();
  const seed = options.seedValue ?? getSeedValueFromEnv(1);
  const limit = options.limit ?? 50;
  const method = options.method ?? "select";
  const params = new URLSearchParams({
    project_key: options.projectKey,
    entity_type: options.entityType,
    seed_value: String(seed),
    limit: String(limit),
    method,
  });
  if (options.filterKey) params.set("filter_key", options.filterKey);
  if (options.filterValues && options.filterValues.length > 0) {
    params.set("filter_values", options.filterValues.join(","));
  }

  const url = `${baseUrl}/datasets/load?${params.toString()}`;
  const resp = await fetch(url, { method: "GET" });
  if (!resp.ok) {
    throw new Error(`Seeded selection request failed: ${resp.status}`);
  }
  const json = await resp.json();
  return (json?.data ?? []) as T[];
}


export async function fetchPoolInfo(projectKey: string, entityType: string): Promise<{ pool_size: number } | null> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/datasets/pool/info?project_key=${encodeURIComponent(projectKey)}&entity_type=${encodeURIComponent(entityType)}`;
  try {
    const resp = await fetch(url, { method: "GET" });
    if (!resp.ok) return null;
    const json = await resp.json();
    if (json && typeof json.pool_size === "number") {
      return { pool_size: json.pool_size as number };
    }
    return null;
  } catch {
    return null;
  }
}



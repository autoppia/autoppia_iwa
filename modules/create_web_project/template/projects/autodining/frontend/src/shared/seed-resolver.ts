/**
 * Centralized seed resolution service client.
 * Calls webs_server API to resolve seeds, with local fallback for SSR/offline.
 * 
 * Supports enable_dynamic URL parameter: ?enable_dynamic=v1,v2
 */

const BOOL_TRUE = ["true", "1", "yes", "y"];

const boolFromEnv = (value?: string | undefined | null): boolean => {
  if (!value) return false;
  return BOOL_TRUE.includes(value.toLowerCase());
};

/**
 * Parse enable_dynamic parameter from URL (e.g., "v1", "v2", "v1,v2", "v1,v2,v3")
 */
function parseEnableDynamicFromUrl(): { v1: boolean; v2: boolean; v3: boolean } | null {
  if (typeof window === "undefined") return null;
  
  const params = new URLSearchParams(window.location.search);
  const enableDynamic = params.get("enable_dynamic");
  
  if (!enableDynamic) return null;
  
  const parts = enableDynamic.toLowerCase().split(",").map(s => s.trim());
  return {
    v1: parts.includes("v1"),
    v2: parts.includes("v2"),
    v3: parts.includes("v3"),
  };
}

/**
 * Get enabled flags from URL parameter or environment variables.
 * Priority: URL parameter > Environment variables
 * 
 * If enable_dynamic is in URL, use it.
 * If not in URL, use environment variables (default deployment config).
 */
function getEnabledFlagsInternal(): { v1: boolean; v2: boolean; v3: boolean } {
  // First, try to get from URL parameter (user explicitly set it)
  const urlFlags = parseEnableDynamicFromUrl();
  if (urlFlags) {
    return urlFlags;
  }
  
  // Fallback to environment variables (deployment default)
  // These are set when deploying: v1=true, v2=true, v3=true by default
  return {
    v1: boolFromEnv(process.env.NEXT_PUBLIC_ENABLE_DYNAMIC_V1) ||
        boolFromEnv(process.env.ENABLE_DYNAMIC_V1),
    v2: boolFromEnv(process.env.NEXT_PUBLIC_ENABLE_DYNAMIC_V2_DB_MODE) ||
        boolFromEnv(process.env.ENABLE_DYNAMIC_V2_DB_MODE),
    v3: boolFromEnv(process.env.NEXT_PUBLIC_ENABLE_DYNAMIC_V3) ||
        boolFromEnv(process.env.ENABLE_DYNAMIC_V3),
  };
}

export type ResolvedSeeds = {
  base: number;
  v1: number | null;
  v2: number | null;
  v3: number | null;
};

const BASE_SEED = {
  min: 1,
  max: 999,
  defaultValue: 1,
};

function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
  const origin = typeof window !== "undefined" ? window.location?.origin : undefined;
  const envIsLocal = envUrl && (envUrl.includes("localhost") || envUrl.includes("127.0.0.1"));
  const originIsLocal = origin && (origin.includes("localhost") || origin.includes("127.0.0.1"));

  if (envUrl && (!(envIsLocal) || originIsLocal)) {
    return envUrl;
  }
  if (origin) {
    return `${origin}/api`;
  }
  return envUrl || "http://app:8090";
}

export function clampBaseSeed(seed: number): number {
  if (Number.isNaN(seed)) return BASE_SEED.defaultValue;
  if (seed < BASE_SEED.min) return BASE_SEED.min;
  if (seed > BASE_SEED.max) return BASE_SEED.max;
  return seed;
}

/**
 * Local fallback seed resolution (same formulas as webs_server).
 * Used when API is unavailable or during SSR.
 */
function resolveSeedsLocal(
  baseSeed: number,
  enabledFlags?: { v1: boolean; v2: boolean; v3: boolean }
): ResolvedSeeds {
  const safeSeed = clampBaseSeed(baseSeed);
  const flags = enabledFlags || getEnabledFlagsInternal();

  const resolved: ResolvedSeeds = {
    base: safeSeed,
    v1: null,
    v2: null,
    v3: null,
  };

  // Same formulas as webs_server/src/seed_resolver.py
  if (flags.v1) {
    resolved.v1 = ((safeSeed * 29 + 7) % 300) + 1;
  }
  if (flags.v2) {
    resolved.v2 = ((safeSeed * 53 + 17) % 300) + 1;
  }
  if (flags.v3) {
    resolved.v3 = ((safeSeed * 71 + 3) % 100) + 1;
  }

  return resolved;
}

/**
 * Resolve seeds using centralized webs_server API.
 * Falls back to local calculation if API is unavailable.
 * 
 * Enabled flags are determined from URL parameter ?enable_dynamic=v1,v2
 * or from environment variables if URL parameter is not present.
 */
export async function resolveSeeds(baseSeed: number): Promise<ResolvedSeeds> {
  const safeSeed = clampBaseSeed(baseSeed);
  const enabledFlags = getEnabledFlagsInternal();

  // During SSR or if API URL is not available, use local fallback
  if (typeof window === "undefined") {
    return resolveSeedsLocal(safeSeed, enabledFlags);
  }

  try {
    const apiUrl = getApiBaseUrl();
    const url = new URL(`${apiUrl}/seeds/resolve`);
    url.searchParams.set("seed", safeSeed.toString());
    url.searchParams.set("v1_enabled", String(enabledFlags.v1));
    url.searchParams.set("v2_enabled", String(enabledFlags.v2));
    url.searchParams.set("v3_enabled", String(enabledFlags.v3));

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Seed resolution API failed: ${response.status}`);
    }

    const data = await response.json();
    return {
      base: data.base ?? safeSeed,
      v1: data.v1 ?? null,
      v2: data.v2 ?? null,
      v3: data.v3 ?? null,
    };
  } catch (error) {
    console.warn("[seed-resolver] API call failed, using local fallback:", error);
    return resolveSeedsLocal(safeSeed, enabledFlags);
  }
}

/**
 * Synchronous version for immediate use (uses local calculation).
 * Use this when you need seeds synchronously (e.g., during initial render).
 */
export function resolveSeedsSync(baseSeed: number): ResolvedSeeds {
  const enabledFlags = getEnabledFlagsInternal();
  return resolveSeedsLocal(baseSeed, enabledFlags);
}

/**
 * Get current enabled flags (from URL or env)
 * Public API for checking what's enabled
 */
export function getEnabledFlags(): { v1: boolean; v2: boolean; v3: boolean } {
  return getEnabledFlagsInternal();
}

export const seedResolverConfig = {
  base: BASE_SEED,
  getEnabledFlags,
};


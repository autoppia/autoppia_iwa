"use client";

import { useEffect, useRef } from "react";
import { useSearchParams, usePathname, useRouter } from "next/navigation";
import { getEnabledFlags } from "@/shared/seed-resolver";

/**
 * Default seed to use when v1 is enabled but no seed is in the URL.
 * This should be set to the seed that shows the web best.
 * Change this value if you find a better-looking seed.
 */
const DEFAULT_V1_SEED = 25;

/**
 * Component that redirects to a default seed URL if:
 * - v1 is enabled
 * - No seed parameter exists in the URL
 *
 * This ensures that v1-enabled sites always have a seed in the URL for consistent behavior.
 * The default seed is set to the one that shows the web best.
 */
export function SeedRedirect() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const hasRedirectedRef = useRef(false);

  useEffect(() => {
    // Only run on client side
    if (typeof window === "undefined") return;

    // Prevent multiple redirects
    if (hasRedirectedRef.current) return;

    // Check if v1 is enabled
    const enabledFlags = getEnabledFlags();
    if (!enabledFlags.v1) {
      // v1 is not enabled, no need to redirect
      return;
    }

    // Check if seed parameter exists in URL
    const seedParam = searchParams.get("seed");
    if (seedParam) {
      // Seed exists in URL, no need to redirect
      return;
    }

    // v1 is enabled but no seed in URL - redirect to add default seed
    hasRedirectedRef.current = true;

    const params = new URLSearchParams(searchParams.toString());
    params.set("seed", DEFAULT_V1_SEED.toString());

    // Preserve enable_dynamic if it exists
    const enableDynamic = searchParams.get("enable_dynamic");
    if (enableDynamic) {
      params.set("enable_dynamic", enableDynamic);
    }

    const newUrl = `${pathname}?${params.toString()}`;

    // Use replace instead of push to avoid adding to history
    router.replace(newUrl);
  }, [searchParams, pathname, router]);

  return null; // This component doesn't render anything
}


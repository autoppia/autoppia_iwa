"use client";

import { useRouter as useNextRouter } from "next/navigation";
import { useSeed } from "@/context/SeedContext";
import { useCallback } from "react";

/**
 * Custom hook that wraps Next.js router and automatically preserves seed parameter
 */
export function useSeedRouter() {
  const router = useNextRouter();
  const { getNavigationUrl } = useSeed();

  const push = useCallback((href: string, options?: any) => {
    const urlWithSeed = getNavigationUrl(href);
    return router.push(urlWithSeed, options);
  }, [router, getNavigationUrl]);

  const replace = useCallback((href: string, options?: any) => {
    const urlWithSeed = getNavigationUrl(href);
    return router.replace(urlWithSeed, options);
  }, [router, getNavigationUrl]);

  return {
    ...router,
    push,
    replace,
  };
}

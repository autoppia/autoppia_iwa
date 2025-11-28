"use client";

import Link from "next/link";
import { useSeed } from "@/context/SeedContext";
import type { ComponentProps } from "react";

interface SeedLinkProps extends Omit<ComponentProps<typeof Link>, 'href'> {
  href: string;
  preserveSeed?: boolean; // Default true, set to false to skip adding seed
}

/**
 * Custom Link component that automatically preserves seed parameter in URLs
 */
export function SeedLink({ href, preserveSeed = true, ...props }: SeedLinkProps) {
  const { getNavigationUrl } = useSeed();

  // If preserveSeed is false or href starts with http (external link), use original href
  const finalHref = (!preserveSeed || href.startsWith('http')) ? href : getNavigationUrl(href);

  return <Link href={finalHref} {...props} />;
}

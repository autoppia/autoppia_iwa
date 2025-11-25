/**
 * useV3Attributes Hook
 *
 * Main hook for V3 anti-scraping system.
 * Provides dynamic IDs, classes, texts, and attributes based on v3 seed.
 */

import { useMemo, useCallback } from 'react';
import { useSeed } from '@/context/SeedContext';
import { generateElementId } from '../utils/id-generator';
import { getTextForElement } from '../utils/text-selector';
import { getClassForElement } from '../utils/class-selector';

const isDynamicEnabled = (): boolean => {
  return process.env.NEXT_PUBLIC_ENABLE_DYNAMIC_V3 === 'true';
};

export function useV3Attributes() {
  const { resolvedSeeds } = useSeed();

  // Get v3 seed (or fallback to v1/base)
  const v3Seed = useMemo(() => {
    return resolvedSeeds.v3 ?? resolvedSeeds.v1 ?? resolvedSeeds.base ?? 1;
  }, [resolvedSeeds.v3, resolvedSeeds.v1, resolvedSeeds.base]);

  const isEnabled = isDynamicEnabled();
  const isActive = isEnabled && v3Seed > 0;

  /**
   * Get dynamic attributes for an element
   * Returns id, data-* attributes, etc.
   */
  const getElementAttributes = useCallback(
    (elementType: string, index: number = 0) => {
      const baseAttrs = {
        id: index > 0 ? `${elementType}-${index}` : elementType,
        'data-element-type': elementType,
      } as Record<string, string>;

      if (!isActive) {
        return baseAttrs;
      }

      const dynamicId = generateElementId(v3Seed, elementType, index);

      return {
        ...baseAttrs,
        id: dynamicId,
        'data-seed': v3Seed.toString(),
        'data-variant': ((v3Seed - 1) % 10).toString(),
        'data-xpath': `//*[@data-element-type='${elementType}' and @data-seed='${v3Seed}']`,
      };
    },
    [v3Seed, isActive]
  );

  /**
   * Get text variant for a key
   */
  const getText = useCallback(
    (key: string, fallback: string): string => {
      if (!isActive) return fallback;
      return getTextForElement(v3Seed, key, fallback);
    },
    [v3Seed, isActive]
  );

  /**
   * Get CSS class variant for a class type
   */
  const getClass = useCallback(
    (classType: string, fallback: string = ''): string => {
      if (!isActive) return fallback;
      return getClassForElement(v3Seed, classType, fallback);
    },
    [v3Seed, isActive]
  );

  /**
   * Generate a unique ID for an element
   */
  const getId = useCallback(
    (elementType: string, index: number = 0): string => {
      if (!isActive) {
        return index > 0 ? `${elementType}-${index}` : elementType;
      }
      return generateElementId(v3Seed, elementType, index);
    },
    [v3Seed, isActive]
  );

  /**
   * Get XPath selector for an element (for testing/debugging)
   */
  const getXPath = useCallback(
    (elementType: string): string => {
      if (!isActive) {
        return `//*[@data-element-type='${elementType}']`;
      }
      return `//*[@data-element-type='${elementType}' and @data-seed='${v3Seed}']`;
    },
    [v3Seed, isActive]
  );

  return {
    v3Seed,
    isEnabled,
    isActive,
    getElementAttributes,
    getText,
    getClass,
    getId,
    getXPath,
  };
}

export type { };

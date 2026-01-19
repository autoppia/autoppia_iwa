/**
 * Variant Selector for V3 Anti-Scraping
 *
 * Selects variants from local component dictionaries or global JSON files
 * Always returns the first variant (original) for seed=1
 */

import idVariantsJson from '../data/id-variants.json';
import classVariantsJson from '../data/class-variants.json';
import textVariantsJson from '../data/text-variants.json';
import { selectVariantIndex } from '../../shared/core';

export const ID_VARIANTS_MAP: Record<string, string[]> = idVariantsJson;
export const CLASS_VARIANTS_MAP: Record<string, string[]> = classVariantsJson;

// Text variants: estructura donde cada key tiene su array de variantes
// Formato: { "key1": ["variant1", "variant2", ...], "key2": [...] }
export const TEXT_VARIANTS_MAP: Record<string, string[]> = textVariantsJson as Record<string, string[]>;

/**
 * Get a variant from a dictionary or global JSONs
 *
 * Works for IDs, classes, and texts - all use the same structure!
 *
 * Simple logic:
 * - If you pass a dictionary, it searches there
 * - If you don't pass a dictionary, it searches in id-variants.json, class-variants.json, and text-variants.json
 *
 * @param seed - The seed value
 * @param key - The key to look up
 * @param variants - Optional dictionary to search in (can be local component dict or global JSON like ID_VARIANTS_MAP)
 * @param fallback - Fallback value if no variants found
 * @returns The selected variant string
 */
export function getVariant(
  seed: number,
  key: string,
  variants?: Record<string, string[]>,
  fallback?: string
): string {
  let selectedVariants: string[] | undefined;

  // 1. If dictionary is provided, search there
  if (variants && key in variants) {
    selectedVariants = variants[key];
  } else if (!variants) {
    // 2. If no dictionary provided, search in all global JSONs (IDs, classes, texts)
    selectedVariants = ID_VARIANTS_MAP[key] || CLASS_VARIANTS_MAP[key] || TEXT_VARIANTS_MAP[key];
  }

  // 3. If no variants found, return fallback or key itself
  if (!selectedVariants || selectedVariants.length === 0) {
    if (fallback !== undefined) {
      return fallback;
    }
    if (typeof window !== "undefined" && process.env.NODE_ENV === "development") {
      console.warn(
        `[variant-selector] No variants found for "${key}", using fallback: "${key}"`
      );
    }
    return key;
  }

  // 4. Select variant based on seed
  if (seed === 1) {
    return selectedVariants[0]; // seed=1 = original (first variant)
  }

  const variantIndex = selectVariantIndex(seed, key, selectedVariants.length);
  return selectedVariants[variantIndex] || selectedVariants[0];
}

/**
 * Text Selector for V3 Anti-Scraping
 *
 * Selects text variants based on seed
 */

import textVariantsJson from '../data/text-variants.json';

type TextKey = string;
type TextVariantMap = Record<TextKey, string>;

const VARIANTS: Record<number, TextVariantMap> = Object.fromEntries(
  Object.entries(textVariantsJson as Record<string, TextVariantMap>).map(([k, v]) => [
    parseInt(k, 10),
    v,
  ])
);

/**
 * Map seed (1-300) to variant index (1-10)
 */
function mapSeedToVariant(seed: number): number {
  if (!seed || seed < 1 || seed > 300) return 1;
  return ((seed - 1) % 10) + 1;
}

/**
 * Get text variant for a specific key and seed
 *
 * @param seed - The v3 seed
 * @param key - Text key (e.g., 'add_to_cart', 'search_placeholder')
 * @param fallback - Fallback text if variant not found
 * @returns The text variant
 */
export function getTextForElement(
  seed: number,
  key: TextKey,
  fallback: string
): string {
  const variantIndex = mapSeedToVariant(seed);
  const variant = VARIANTS[variantIndex];

  return (variant && variant[key]) || fallback;
}

/**
 * Get all text variants for a specific seed
 */
export function getAllTextsForSeed(seed: number): TextVariantMap {
  const variantIndex = mapSeedToVariant(seed);
  return VARIANTS[variantIndex] || VARIANTS[1];
}

/**
 * Get available text keys
 */
export function getAvailableTextKeys(): TextKey[] {
  const firstVariant = VARIANTS[1] || {};
  return Object.keys(firstVariant);
}

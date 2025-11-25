/**
 * ID Generator for V3 Anti-Scraping
 *
 * Generates semantic, non-predictable IDs based on seed
 */

import semanticIdsJson from '../data/semantic-ids.json';

const SEMANTIC_ID_MAP: Record<string, string[]> = semanticIdsJson;

/**
 * Map seed (1-300) to variant index (0-9)
 */
function mapSeedToVariant(seed: number): number {
  if (!seed || seed < 1) return 0;
  return ((seed - 1) % 10);
}

/**
 * Generate a semantic ID for an element based on seed
 *
 * @param seed - The v3 seed
 * @param elementType - Type of element (e.g., 'search-input', 'cart-button')
 * @param index - Optional index for multiple instances
 * @returns A semantic ID string
 */
export function generateElementId(
  seed: number,
  elementType: string,
  index: number = 0
): string {
  const variants = SEMANTIC_ID_MAP[elementType];

  if (!variants || variants.length === 0) {
    // Fallback to basic ID
    return index > 0 ? `${elementType}-${index}` : elementType;
  }

  const variantIndex = mapSeedToVariant(seed);
  const baseId = variants[variantIndex] || variants[0];

  // Add index suffix if needed
  return index > 0 ? `${baseId}-${index}` : baseId;
}

/**
 * Get all available element types
 */
export function getAvailableElementTypes(): string[] {
  return Object.keys(SEMANTIC_ID_MAP);
}

/**
 * Check if an element type has semantic variants
 */
export function hasSemanticVariants(elementType: string): boolean {
  return elementType in SEMANTIC_ID_MAP;
}

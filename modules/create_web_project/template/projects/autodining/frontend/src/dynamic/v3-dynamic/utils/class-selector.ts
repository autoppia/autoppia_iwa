/**
 * Class Selector for V3 Anti-Scraping
 *
 * Selects CSS class variants based on seed
 */

import classVariantsJson from '../data/class-variants.json';

const CLASS_VARIANTS_MAP: Record<string, string[]> = classVariantsJson;

/**
 * Map seed (1-300) to variant index (0-9)
 */
function mapSeedToVariant(seed: number): number {
  if (!seed || seed < 1) return 0;
  return ((seed - 1) % 10);
}

/**
 * Get CSS class variant for a specific class type and seed
 *
 * @param seed - The v3 seed
 * @param classType - Class type (e.g., 'button-primary', 'card', 'nav-link')
 * @param fallback - Fallback class if variant not found
 * @returns The class variant
 */
export function getClassForElement(
  seed: number,
  classType: string,
  fallback: string = ''
): string {
  const variants = CLASS_VARIANTS_MAP[classType];

  if (!variants || variants.length === 0) {
    return fallback;
  }

  const variantIndex = mapSeedToVariant(seed);
  return variants[variantIndex] || variants[0] || fallback;
}

/**
 * Get multiple class variants at once
 *
 * @param seed - The v3 seed
 * @param classTypes - Array of class types
 * @returns Object mapping class types to their variants
 */
export function getClassesForElements(
  seed: number,
  classTypes: string[]
): Record<string, string> {
  return classTypes.reduce((acc, classType) => {
    acc[classType] = getClassForElement(seed, classType);
    return acc;
  }, {} as Record<string, string>);
}

/**
 * Get available class types
 */
export function getAvailableClassTypes(): string[] {
  return Object.keys(CLASS_VARIANTS_MAP);
}

/**
 * Check if a class type has variants
 */
export function hasClassVariants(classType: string): boolean {
  return classType in CLASS_VARIANTS_MAP;
}

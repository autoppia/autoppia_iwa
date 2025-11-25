/**
 * V3 Anti-Scraping System
 *
 * Dynamically changes IDs, classes, texts, and attributes to confuse scrapers.
 * All changes are seed-based and deterministic.
 */

// Main hook
export { useV3Attributes } from './hooks/useV3Attributes';

// Utilities
export { generateElementId, getAvailableElementTypes, hasSemanticVariants } from './utils/id-generator';
export { getTextForElement, getAllTextsForSeed, getAvailableTextKeys } from './utils/text-selector';
export { getClassForElement, getClassesForElements, getAvailableClassTypes, hasClassVariants } from './utils/class-selector';

// Types (if needed later)
export type V3Attributes = {
  id: string;
  'data-element-type': string;
  'data-seed': string;
  'data-variant': string;
  'data-xpath': string;
};

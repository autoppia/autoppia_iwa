/**
 * CORE - Base functions and primary useDynamicSystem() hook
 * 
 * Core helpers for variants and the centralized hook
 */

"use client";

import { useMemo } from "react";
import { useSeed } from "@/context/SeedContext";
import { applyV1Wrapper } from "../v1/add-wrap-decoy";
import { isV3Enabled } from "./flags";
import { getVariant, ID_VARIANTS_MAP, CLASS_VARIANTS_MAP } from "../v3/utils/variant-selector";
import { generateDynamicOrder } from "../v1/change-order-elements";
import type { ReactNode } from "react";

// ============================================================================
// BASE FUNCTIONS
// ============================================================================

/**
 * Generates a deterministic hash for a string
 * Optimized version that avoids overly large numbers
 */
export function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    const char = value.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer (avoids overflow)
  }
  return Math.abs(hash);
}

/**
 * Selects the index of a variant based on seed and key
 * Internal helper used by getVariant to calculate which variant to use
 * 
 * @param seed - The base seed (1-999)
 * @param key - Unique identifier for the component
 * @param count - Number of available variants (returns 0 to count-1)
 * @returns Variant index (0, 1, 2, ..., count-1)
 */
export function selectVariantIndex(seed: number, key: string, count: number): number {
  if (count <= 1) return 0;
  
  // Combine seed and key into a single string and hash it
  // This ensures each (seed, key) combination produces a unique hash
  const combinedInput = `${key}:${seed}`;
  const combinedHash = hashString(combinedInput);
  
  // Reduce the hash to the available variant range
  // Use direct modulus for maximum distribution
  return Math.abs(combinedHash) % count;
}

/**
 * Generates a unique ID based on seed and key
 */
export function generateId(seed: number, key: string, prefix = "dyn"): string {
  return `${prefix}-${key}-${Math.abs(seed + hashString(key)) % 9999}`;
}

// ============================================================================
// MAIN HOOK: useDynamicSystem()
// ============================================================================

/**
 * Centralized hook that unifies V1 (wrappers/decoy) and V3 (attributes/text)
 * 
 * Usage:
 *   const dyn = useDynamicSystem();
 *   dyn.v1.addWrapDecoy()         // V1: Adds wrappers and decoys
 *   dyn.v1.changeOrderElements()  // V1: Changes element order
 *   dyn.v3.getVariant()           // V3: Gets variants (IDs, classes, texts)
 * 
 * It behaves the same even if V1/V3 are OFF:
 * - If V1 is OFF: dyn.v1.addWrapDecoy() returns children unchanged
 * - If V3 is OFF: dyn.getVariant() returns the fallback or key
 * 
 * The seed is read automatically from SeedContext (which reads it from the URL).
 * You do not need to pass the seed manually.
 */
export function useDynamicSystem() {
  const { seed } = useSeed();
  
  return useMemo(() => ({
    seed,
    
    /**
     * V1: DOM structure (wrappers, decoys, and ordering)
     * Breaks XPath by adding invisible elements and changing order
     */
    v1: {
      /**
       * Adds wrapper and decoy to break XPath
       * 
       * Always uses 2 wrapper variants (0=none, 1=with) and 3 decoy variants (0=none, 1=before, 2=after)
       * 
       * @param componentKey - Unique component identifier (e.g. "restaurant-card", "search-button")
       * @param children - Element to wrap
       * @param reactKey - Optional React key
       * 
       * If V1 is OFF, returns children unchanged
       */
      addWrapDecoy: (
        componentKey: string,
        children: ReactNode,
        reactKey?: string
      ) => applyV1Wrapper(seed, componentKey, children, reactKey),
      
      /**
       * Changes the dynamic order of element arrays
       * @param key - Unique identifier (e.g. "restaurant-cards", "featured-restaurants")
       * @param count - Number of elements (e.g. 4, 6, 10)
       * @returns Array of reordered indexes
       */
      changeOrderElements: (key: string, count: number) => 
        generateDynamicOrder(seed, key, count),
    },
    
    /**
     * V3: Variants (IDs, classes, texts)
     * Single function for everything - same logic, same structure
     */
    v3: {
      /**
       * Get variant (IDs, classes, texts)
       * 
       * @param key - The key to look up
       * @param variants - Optional dictionary (component-local or global like ID_VARIANTS_MAP)
       * @param fallback - Default value if none found
       * @returns The selected variant (string)
       * 
       * Examples:
       *   dyn.v3.getVariant("section", dynamicV3IdsVariants)  // Local IDs
       *   dyn.v3.getVariant("button", CLASS_VARIANTS_MAP)  // Global classes
       *   dyn.v3.getVariant("search_placeholder", undefined, "Search...")  // Texts (searches TEXT_VARIANTS_MAP)
       *   dyn.v3.getVariant("feature_1_title", dynamicV3TextVariants)  // Local texts
       */
      getVariant: (
        key: string,
        variants?: Record<string, string[]>,
        fallback?: string
      ) => {
        // Si V3 está deshabilitado, devolver fallback o primera variante disponible
        if (!isV3Enabled()) {
          if (fallback !== undefined) return fallback;
          // Si hay variantes locales, devolver la primera
          if (variants && key in variants && variants[key].length > 0) {
            return variants[key][0];
          }
          // Si no hay variantes, devolver la key (pero esto no debería pasar)
          return key;
        }
        return getVariant(seed, key, variants, fallback);
      },
    },
    
    /**
     * Utility: select variant index for custom logic
     */
    selectVariantIndex: (key: string, count: number) => 
      selectVariantIndex(seed, key, count),
  }), [seed]);
}


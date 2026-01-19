/**
 * Utilities to generate dynamic ordering of elements (V1)
 *
 * Generates different orders based on the seed without hardcoding every permutation
 * This functionality belongs to V1 because it modifies element structure/order
 */

import { selectVariantIndex } from "../shared/core";

/**
 * Generates a dynamic order for an array of elements
 *
 * @param seed - Base seed (1-999)
 * @param key - Unique identifier for this set of elements (e.g. "featured-restaurants", "booking-cards")
 * @param count - Number of elements (e.g. 3, 4, 6)
 * @returns Array of reordered indexes (e.g. [0,1,2] or [2,0,1] for count=3)
 */
export function generateDynamicOrder(
  seed: number,
  key: string,
  count: number
): number[] {
  // Seed 1 = original order (0, 1, 2, ..., count-1)
  if (seed === 1) {
    return Array.from({ length: count }, (_, i) => i);
  }

  // For other seeds, generate dynamic order
  // Use a deterministic hash function to generate the order

  // Generate multiple order variants using different offsets
  const orderVariants: number[][] = [];

  // Generate variants using different strategies:
  // 1. Rotations
  for (let offset = 0; offset < count; offset++) {
    const rotated = Array.from({ length: count }, (_, i) => (i + offset) % count);
    orderVariants.push(rotated);
  }

  // 2. Pair swaps
  for (let i = 0; i < count - 1; i++) {
    const swapped = Array.from({ length: count }, (_, j) => {
      if (j === i) return i + 1;
      if (j === i + 1) return i;
      return j;
    });
    // Only add if it differs from the original order
    if (!arraysEqual(swapped, Array.from({ length: count }, (_, j) => j))) {
      orderVariants.push(swapped);
    }
  }

  // 3. Partial reversals
  for (let split = 1; split < count; split++) {
    const reversed = [
      ...Array.from({ length: split }, (_, i) => split - 1 - i),
      ...Array.from({ length: count - split }, (_, i) => split + i)
    ];
    if (!arraysEqual(reversed, Array.from({ length: count }, (_, j) => j))) {
      orderVariants.push(reversed);
    }
  }

  // 4. Deterministic shuffle using hash
  const hashBased = generateHashBasedOrder(seed, key, count);
  if (!arraysEqual(hashBased, Array.from({ length: count }, (_, j) => j))) {
    orderVariants.push(hashBased);
  }

  // Remove duplicates
  const uniqueVariants = removeDuplicateOrders(orderVariants);

  // If there are no variants, return original order
  if (uniqueVariants.length === 0) {
    return Array.from({ length: count }, (_, i) => i);
  }

  // Select variant using selectVariantIndex
  const variantIndex = selectVariantIndex(seed, key, uniqueVariants.length);
  return uniqueVariants[variantIndex];
}

/**
 * Generates a hash-based order for maximum variation
 */
function generateHashBasedOrder(seed: number, key: string, count: number): number[] {
  // Combine seed and key to generate hash
  const combined = `${key}:${seed}`;
  let hash = 0;
  for (let i = 0; i < combined.length; i++) {
    const char = combined.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }

  // Generate order using deterministic Fisher-Yates shuffle
  const order = Array.from({ length: count }, (_, i) => i);
  for (let i = count - 1; i > 0; i--) {
    const j = Math.abs(hash + i * 7919) % (i + 1);
    [order[i], order[j]] = [order[j], order[i]];
  }

  return order;
}

/**
 * Compares two arrays to see if they are equal
 */
function arraysEqual(a: number[], b: number[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((val, i) => val === b[i]);
}

/**
 * Removes duplicate orders from an array
 */
function removeDuplicateOrders(orders: number[][]): number[][] {
  const seen = new Set<string>();
  const unique: number[][] = [];

  for (const order of orders) {
    const key = order.join(',');
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(order);
    }
  }

  return unique;
}

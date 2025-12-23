# Tests Documentation

This directory contains automated tests for validating the dynamic system and event coverage in the web application.

## Available Tests

### 1. `test-dynamic-system.js`

Comprehensive test suite that validates the dynamic anti-scraping system (V1 and V3). It verifies file structure, variant definitions, determinism, seed variation, and real code usage.

#### Test 1: File Structure
**Purpose**: Verifies that all required dynamic system files exist.

**What it checks**:
- Core dynamic system files (`core.ts`, `variant-selector.ts`)
- V1 implementation files (`add-wrap-decoy.ts`, `change-order-elements.ts`)
- V3 variant JSON files (`id-variants.json`, `class-variants.json`, `text-variants.json`)

**Why it matters**: Ensures the dynamic system is properly set up and all dependencies are present.

---

#### Test 2: Variants in JSON Files
**Purpose**: Analyzes the variant JSON files and reports statistics.

**What it checks**:
- Number of keys in `id-variants.json`, `class-variants.json`, and `text-variants.json`
- Whether each key has at least 3 variants (configurable via `MIN_REQUIREMENTS.minVariants`)

**Why it matters**: Provides visibility into available variants. Note: This test is informational only; actual usage is verified in Test 5.

---

#### Test 3: Determinism
**Purpose**: Verifies that the same seed always produces the same result (critical for reproducibility).

**What it checks**:
- For a given `(seed, key, count)` combination, the function `selectVariantIndex()` always returns the same `variantIndex`
- Tests multiple seed/key combinations to ensure consistency

**Why it matters**: 
- **Critical requirement**: Same seed must always produce the same variant
- Enables reproducible testing and debugging
- Ensures users see consistent results when sharing URLs with the same seed

**Example**:
```
seed=42, key="movie-card" → variantIndex: 3 (always)
seed=42, key="movie-card" → variantIndex: 3 (always) ✅
```

---

#### Test 4: Seed Variation
**Purpose**: Verifies that different seeds produce different results (essential for anti-scraping effectiveness).

**What it checks**:
- Tests 11 different seeds (1, 2, 3, 5, 10, 25, 50, 100, 250, 500, 999) across multiple keys
- Calculates variation ratio: how many unique variant indices are produced
- Requires at least 50% average variation and 3 out of 4 keys with good variation

**Why it matters**:
- **Anti-scraping effectiveness**: If all seeds produce the same result, the system doesn't work
- Ensures good distribution: different seeds should map to different variants
- Some collisions are normal (mathematically inevitable when seeds > variants), but we need good overall distribution

**Example**:
```
seed=1  → variantIndex: 3
seed=2  → variantIndex: 2  ✅ Different
seed=3  → variantIndex: 1  ✅ Different
```

**Note**: It's normal for different hashes to map to the same index (modulo collisions). What matters is that:
- Same seed always produces the same result (Test 3)
- Different seeds produce different results most of the time (Test 4)

---

#### Test 5: Real Usage in Code
**Purpose**: Counts actual usage of dynamic system functions in the source code (not just JSON keys).

**What it checks**:
- **V1 `addWrapDecoy`**: Counts calls to `dyn.v1.addWrapDecoy()` or `addWrapDecoy()`
- **V1 `changeOrderElements`**: Counts calls to `dyn.v1.changeOrderElements()` or `changeOrderElements()`
- **V3 IDs**: Counts `getVariant()` calls with `ID_VARIANTS_MAP`
- **V3 Classes**: Counts `getVariant()` calls with `CLASS_VARIANTS_MAP`
- **V3 Texts**: Counts `getVariant()` calls for text variants

**Minimum requirements** (configurable):
- V1 addWrapDecoy: 20 uses
- V1 changeOrderElements: 5 uses
- V3 IDs: 25 uses
- V3 Classes: 15 uses
- V3 Texts: 30 uses

**Why it matters**: 
- Ensures the dynamic system is actually being used in the codebase
- Prevents "dead" variant definitions (keys in JSON that are never used)
- Validates that the anti-scraping system has sufficient coverage

---

#### Test 6: Event Coverage
**Purpose**: Verifies that all events defined in `EVENT_TYPES` are being used in the codebase.

**What it checks**:
- Finds the `events.ts` file (in `src/library/` or `src/lib/`)
- Extracts all event names from `EVENT_TYPES`
- Searches for usage of each event in the codebase:
  - `logEvent(EVENT_TYPES.XXX, ...)`
  - `logEvent(EVENT_TYPES['XXX'], ...)`
  - Direct string usage in `logEvent()` calls
- **Requires 100% coverage**: All events must be used

**Why it matters**:
- Prevents unused event definitions
- Ensures all events are actually triggered in the application
- Critical for event-based validation systems

---

#### Test 7: DOM Usage (Browser Only)
**Purpose**: Counts dynamic elements in the rendered DOM (only works in browser).

**What it checks**:
- V1 wrappers/decoys: Counts elements with `[data-dyn-wrap]` and `[data-decoy]` attributes
- V3 IDs: Counts unique IDs in the DOM

**Why it matters**: Validates that the dynamic system is actually rendering in the browser.

---

### 2. `test-events.js`

Standalone test focused exclusively on event coverage validation.

**Purpose**: Validates that all events defined in `EVENT_TYPES` are being used (100% coverage required).

**What it checks**:
- Same as Test 6 in `test-dynamic-system.js`, but as a separate, focused test
- Useful for quick event validation without running the full dynamic system test suite

**Why it exists**: 
- Can be run independently for faster feedback on event coverage
- Useful in CI/CD pipelines where you only want to check events

---

## Running the Tests

### From Command Line

```bash
# Run dynamic system tests
node tests/test-dynamic-system.js

# Run event coverage test
node tests/test-events.js
```

### From Browser

For `test-dynamic-system.js` only:
1. Open browser console (F12)
2. Copy the contents of `test-dynamic-system.js`
3. Paste into console
4. Run `testDynamicSystem()`

---

## Configuration

### Minimum Requirements

Edit `MIN_REQUIREMENTS` in `test-dynamic-system.js`:

```javascript
const MIN_REQUIREMENTS = {
  v1AddWrapDecoy: 20,      // Minimum addWrapDecoy usages
  v1ChangeOrder: 5,         // Minimum changeOrderElements usages
  v3Ids: 25,                // Minimum getVariant with ID_VARIANTS_MAP usages
  v3Classes: 15,            // Minimum getVariant with CLASS_VARIANTS_MAP usages
  v3Texts: 30,              // Minimum getVariant for texts usages
  minVariants: 3,           // Minimum variants per key in JSONs
};
```

---

## Understanding Test Results

### ✅ Success
All tests pass and the system meets minimum requirements.

### ⚠️ Warnings
- Some tests may show warnings (e.g., keys with few variants)
- These are informational and don't fail the test

### ❌ Failures
- Missing required files
- Insufficient usage counts
- Determinism failures (same seed produces different results)
- Poor seed variation (< 50%)
- Events not being used (not 100% coverage)

---

## Key Concepts

### Determinism vs Variation

- **Determinism** (Test 3): Same seed = same result (always)
  - Critical: Must never fail
  - Enables reproducible testing

- **Variation** (Test 4): Different seeds = different results (most of the time)
  - Important: Ensures anti-scraping effectiveness
  - Some collisions are normal (mathematically inevitable)

### Real Usage vs JSON Keys

- **JSON Keys** (Test 2): What variants are *defined*
- **Real Usage** (Test 5): What variants are *actually used* in code
- Both matter, but real usage is what counts for anti-scraping effectiveness

---

## Troubleshooting

### Test fails with "File not found"
- Ensure you're running from the project root
- Check that `src/dynamic/` directory structure exists

### Low variation in Test 4
- This is normal if you have fewer variants than seeds tested
- Consider adding more variants to improve distribution

### Events not found
- Check that `events.ts` is in `src/library/` or `src/lib/`
- Verify `EVENT_TYPES` is exported correctly

---

## Contributing

When adding new dynamic features:
1. Update minimum requirements if needed
2. Ensure new features are used in code (Test 5 will catch this)
3. Add new events to `EVENT_TYPES` and use them (Test 6 will catch unused events)


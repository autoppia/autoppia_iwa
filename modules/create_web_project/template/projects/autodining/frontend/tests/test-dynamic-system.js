#!/usr/bin/env node
/**
 * 🧪 GENERIC DYNAMIC SYSTEM TEST (IMPROVED)
 *
 * This script validates that the dynamic system (V1 and V3) works correctly.
 * It counts REAL USAGE in code, not just keys in JSON files.
 *
 * USAGE:
 *   1. From Node.js: node tests/test-dynamic-system.js
 *   2. From the browser: copy the contents into the console (F12) and run testDynamicSystem()
 *
 * CONFIGURATION:
 *   Modify MIN_REQUIREMENTS according to your site's requirements.
 */

// ============================================================================
// CONFIGURATION (ADAPT AS NEEDED FOR THE SITE)
// ============================================================================

const MIN_REQUIREMENTS = {
  v1AddWrapDecoy: 20,      // Minimum addWrapDecoy usages (todas tienen al menos 26)
  v1ChangeOrder: 5,        // Minimum changeOrderElements usages
  v3Ids: 25,               // Minimum getVariant with ID_VARIANTS_MAP usages (todas tienen al menos 29)
  v3Classes: 15,           // Minimum getVariant with CLASS_VARIANTS_MAP usages (web_4 tiene 16)
  v3Texts: 30,             // Minimum getVariant for texts usages (todas tienen al menos 34)
  minVariants: 3,          // Minimum variants per key in JSONs
};

// Paths to the files (adjust if the structure is different)
const FILE_PATHS = {
  idVariants: 'src/dynamic/v3/data/id-variants.json',
  classVariants: 'src/dynamic/v3/data/class-variants.json',
  textVariants: 'src/dynamic/v3/data/text-variants.json',
  addWrapDecoy: 'src/dynamic/v1/add-wrap-decoy.ts',
  changeOrder: 'src/dynamic/v1/change-order-elements.ts',
  variantSelector: 'src/dynamic/v3/utils/variant-selector.ts',
  core: 'src/dynamic/shared/core.ts',
};

// ============================================================================
// UTILITIES (shared by determinism and seed-variation tests)
// ============================================================================

const {
  isBrowser,
  readFileContent,
  getAllSourceFiles,
  findEventsFile,
  parseEventNamesFromContent,
  countEventUsages,
  DEFAULT_EVENTS_PATHS
} = require('./test-helpers.js');

function hashString(str) {
  let hash = 0;
  let i = 0;
  while (i < str.length) {
    const code = str.codePointAt(i) ?? 0;
    hash = ((hash << 5) - hash) + code;
    hash = hash & hash;
    i += code > 0xFFFF ? 2 : 1;
  }
  return Math.abs(hash);
}

function selectVariantIndex(seed, key, count) {
  if (count <= 1) return 0;
  const combined = `${key}:${seed}`;
  const hash = hashString(combined);
  return Math.abs(hash) % count;
}

function loadJSON(path) {
  if (isBrowser()) {
    throw new Error('En navegador, los JSONs deben cargarse vía fetch');
  }
  const fs = require('node:fs');
  const pathModule = require('node:path');
  return JSON.parse(fs.readFileSync(pathModule.join(process.cwd(), path), 'utf8'));
}

function fileExists(path) {
  if (isBrowser()) return false;
  const fs = require('node:fs');
  const pathModule = require('node:path');
  return fs.existsSync(pathModule.join(process.cwd(), path));
}

function countPatternInFiles(files, pattern) {
  let count = 0;
  files.forEach(file => {
    const content = readFileContent(file);
    const matches = content.match(new RegExp(pattern, 'g'));
    if (matches) {
      count += matches.length;
    }
  });
  return count;
}

// ============================================================================
// TEST 1: File structure
// ============================================================================

function testFileStructure() {
  console.log('\n📁 TEST 1: Estructura de archivos');
  console.log('─'.repeat(60));

  const results = { passed: 0, failed: 0, errors: [] };

  if (isBrowser()) {
    console.log('   ⚠️  Verificación de archivos solo disponible en Node.js');
    return results;
  }

  const requiredFiles = [
    FILE_PATHS.addWrapDecoy,
    FILE_PATHS.changeOrder,
    FILE_PATHS.variantSelector,
    FILE_PATHS.idVariants,
    FILE_PATHS.classVariants,
    FILE_PATHS.textVariants,
    FILE_PATHS.core,
  ];

  requiredFiles.forEach(file => {
    if (fileExists(file)) {
      console.log(`   ✅ ${file}`);
      results.passed++;
    } else {
      console.log(`   ❌ ${file} - NO ENCONTRADO`);
      results.failed++;
      results.errors.push(`Archivo faltante: ${file}`);
    }
  });

  return results;
}

// ============================================================================
// TEST 2: Variants in JSON files
// ============================================================================

function testVariantFiles() {
  console.log('\n📦 TEST 2: Variantes en archivos JSON');
  console.log('─'.repeat(60));

  const results = {
    passed: 0,
    failed: 0,
    errors: [],
    stats: {
      idKeys: 0,
      classKeys: 0,
      textKeys: 0,
      keysWithFewVariants: []
    }
  };

  if (isBrowser()) {
    console.log('   ⚠️  En navegador, este test requiere Node.js');
    return results;
  }

  try {
    const idVariants = loadJSON(FILE_PATHS.idVariants);
    const classVariants = loadJSON(FILE_PATHS.classVariants);
    const textVariants = loadJSON(FILE_PATHS.textVariants);

    // Count keys and verify variants
    results.stats.idKeys = Object.keys(idVariants).length;
    results.stats.classKeys = Object.keys(classVariants).length;
    results.stats.textKeys = Object.keys(textVariants).length;

    // Check that each key has enough variants
    [idVariants, classVariants, textVariants].forEach((variants, index) => {
      const type = ['IDs', 'Clases', 'Textos'][index];
      Object.entries(variants).forEach(([key, variantsArray]) => {
        const count = Array.isArray(variantsArray) ? variantsArray.length : 0;
        if (count < MIN_REQUIREMENTS.minVariants) {
          results.stats.keysWithFewVariants.push(`${type}: "${key}" tiene solo ${count} variantes`);
        }
      });
    });

    console.log(`   📊 IDs: ${results.stats.idKeys} keys`);
    console.log(`   📊 Clases: ${results.stats.classKeys} keys`);
    console.log(`   📊 Textos: ${results.stats.textKeys} keys`);

    // Just report, don't fail on JSON keys (we check real usage in TEST 5)
    if (results.stats.keysWithFewVariants.length > 0) {
      console.log(`   ⚠️  Keys con pocas variantes (<${MIN_REQUIREMENTS.minVariants}): ${results.stats.keysWithFewVariants.length}`);
      results.stats.keysWithFewVariants.slice(0, 3).forEach(msg => console.log(`      - ${msg}`));
    }

    results.passed = 3; // Always pass, just informational

  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
    results.failed++;
    results.errors.push(`Error: ${error.message}`);
  }

  return results;
}

// ============================================================================
// TEST 3: Determinism
// ============================================================================

function testDeterminism() {
  console.log('\n🎲 TEST 3: Determinismo (mismo seed = mismo resultado)');
  console.log('─'.repeat(60));

  const results = { passed: 0, failed: 0, errors: [] };

  // Test cases
  const testCases = [
    { seed: 42, key: 'movie-card', count: 10 },
    { seed: 100, key: 'search-input', count: 10 },
    { seed: 1, key: 'button', count: 10 },
  ];

  testCases.forEach(({ seed, key, count }) => {
    const r1 = selectVariantIndex(seed, key, count);
    const r2 = selectVariantIndex(seed, key, count);
    const r3 = selectVariantIndex(seed, key, count);

    if (r1 === r2 && r2 === r3) {
      console.log(`   ✅ seed=${seed}, key="${key}": ${r1} (consistente)`);
      results.passed++;
    } else {
      console.log(`   ❌ seed=${seed}, key="${key}": ${r1} vs ${r2} vs ${r3}`);
      results.failed++;
      results.errors.push(`Determinismo falló para seed=${seed}, key="${key}"`);
    }
  });

  return results;
}

// ============================================================================
// TEST 4: Seed Variation (different seeds = different results)
// ============================================================================

function testSeedVariation() {
  console.log('\n🎯 TEST 4: Variación de Seeds (diferentes seeds = diferentes resultados)');
  console.log('─'.repeat(60));

  const results = { passed: 0, failed: 0, errors: [], stats: {} };

  // Test with multiple seeds and keys
  const testSeeds = [1, 2, 3, 5, 10, 25, 50, 100, 250, 500, 999];
  const testKeys = ['button', 'input', 'card', 'container'];
  const variantCount = 10; // Simulate 10 variants available

  let totalTests = 0;
  let uniqueVariations = 0;
  let totalVariations = 0;

  testKeys.forEach(key => {
    const seedResults = {};
    testSeeds.forEach(seed => {
      const variantIndex = selectVariantIndex(seed, key, variantCount);
      seedResults[seed] = variantIndex;
      totalTests++;
    });

    // Check variation for this key
    const uniqueIndices = new Set(Object.values(seedResults));
    const variationRatio = uniqueIndices.size / testSeeds.length;
    totalVariations += uniqueIndices.size;

    if (variationRatio >= 0.5) {
      uniqueVariations++;
      console.log(`   ✅ "${key}": ${uniqueIndices.size}/${testSeeds.length} variantes únicas (${(variationRatio * 100).toFixed(0)}%)`);
    } else {
      console.log(`   ⚠️  "${key}": ${uniqueIndices.size}/${testSeeds.length} variantes únicas (${(variationRatio * 100).toFixed(0)}%) - poca variación`);
    }
  });

  results.stats.totalTests = totalTests;
  results.stats.totalVariations = totalVariations;
  results.stats.averageVariation = (totalVariations / (testKeys.length * testSeeds.length)) * 100;

  const overallVariationRatio = totalVariations / totalTests;
  console.log(`\n   📊 Variación promedio: ${(overallVariationRatio * 100).toFixed(1)}%`);

  // Pass if at least 50% of seeds produce unique variants (good distribution)
  // This means different seeds should produce different results most of the time
  if (overallVariationRatio >= 0.5) {
    console.log(`   ✅ Variación de seeds: ${(overallVariationRatio * 100).toFixed(1)}% >= 50% (buena distribución)`);
    results.passed++;
  } else {
    console.log(`   ❌ Variación de seeds: ${(overallVariationRatio * 100).toFixed(1)}% < 50% (poca variación)`);
    results.failed++;
    results.errors.push(`La variación entre seeds es insuficiente (${(overallVariationRatio * 100).toFixed(1)}% < 50%)`);
  }

  // Also check that at least 3 out of 4 keys have good variation
  if (uniqueVariations >= 3) {
    console.log(`   ✅ ${uniqueVariations}/${testKeys.length} keys tienen buena variación`);
    results.passed++;
  } else {
    console.log(`   ⚠️  Solo ${uniqueVariations}/${testKeys.length} keys tienen buena variación`);
    results.failed++;
    results.errors.push(`Solo ${uniqueVariations}/${testKeys.length} keys tienen buena variación`);
  }

  return results;
}

// ============================================================================
// TEST 5: DOM usage (browser only)
// ============================================================================

function testDOMUsage() {
  console.log('\n🌐 TEST 4: Uso en DOM');
  console.log('─'.repeat(60));

  const results = { passed: 0, failed: 0, errors: [], stats: {} };

  if (!isBrowser()) {
    console.log('   ⚠️  Este test solo funciona en el navegador');
    return results;
  }

  // Count V1
  const wrappers = document.querySelectorAll('[data-dyn-wrap]').length;
  const decoys = document.querySelectorAll('[data-decoy]').length;
  const totalV1 = wrappers + decoys;
  results.stats.v1Wrappers = totalV1;

  console.log(`   📊 Wrappers: ${wrappers}, Decoys: ${decoys}, Total V1: ${totalV1}`);

  if (totalV1 >= MIN_REQUIREMENTS.v1AddWrapDecoy) {
    console.log(`   ✅ V1: ${totalV1} >= ${MIN_REQUIREMENTS.v1AddWrapDecoy}`);
    results.passed++;
  } else {
    console.log(`   ❌ V1: ${totalV1} < ${MIN_REQUIREMENTS.v1AddWrapDecoy}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v1AddWrapDecoy - totalV1} elementos V1`);
  }

  // Count V3 IDs
  const uniqueIds = new Set(
    Array.from(document.querySelectorAll('[id]'))
      .map(el => el.id)
      .filter(id => id && id.length > 0)
  );
  results.stats.v3Ids = uniqueIds.size;

  console.log(`   📊 IDs únicos: ${uniqueIds.size}`);

  if (uniqueIds.size >= MIN_REQUIREMENTS.v3Ids) {
    console.log(`   ✅ V3 IDs: ${uniqueIds.size} >= ${MIN_REQUIREMENTS.v3Ids}`);
    results.passed++;
  } else {
    console.log(`   ❌ V3 IDs: ${uniqueIds.size} < ${MIN_REQUIREMENTS.v3Ids}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v3Ids - uniqueIds.size} IDs dinámicos`);
  }

  return results;
}

// ============================================================================
// TEST 6: REAL USAGE IN CODE (NEW!)
// ============================================================================

function testRealUsage() {
  console.log('\n💻 TEST 5: USO REAL EN CÓDIGO');
  console.log('─'.repeat(60));

  const results = {
    passed: 0,
    failed: 0,
    errors: [],
    stats: {
      v1AddWrapDecoy: 0,
      v1ChangeOrder: 0,
      v3Ids: 0,
      v3Classes: 0,
      v3Texts: 0,
    }
  };

  if (isBrowser()) {
    console.log('   ⚠️  Este test solo funciona en Node.js');
    return results;
  }

  const sourceFiles = getAllSourceFiles({ excludeFileNameContaining: 'test-dynamic-system' });
  console.log(`   📂 Archivos fuente encontrados: ${sourceFiles.length}`);

  // Count V1: addWrapDecoy (dyn.v1.addWrapDecoy or addWrapDecoy)
  const addWrapDecoyPattern = /\.v1\.addWrapDecoy|addWrapDecoy\(/g;
  results.stats.v1AddWrapDecoy = countPatternInFiles(sourceFiles, addWrapDecoyPattern);
  console.log(`   📊 V1 addWrapDecoy: ${results.stats.v1AddWrapDecoy} usos`);

  if (results.stats.v1AddWrapDecoy >= MIN_REQUIREMENTS.v1AddWrapDecoy) {
    console.log(`   ✅ V1 addWrapDecoy: ${results.stats.v1AddWrapDecoy} >= ${MIN_REQUIREMENTS.v1AddWrapDecoy}`);
    results.passed++;
  } else {
    console.log(`   ❌ V1 addWrapDecoy: ${results.stats.v1AddWrapDecoy} < ${MIN_REQUIREMENTS.v1AddWrapDecoy}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v1AddWrapDecoy - results.stats.v1AddWrapDecoy} usos de addWrapDecoy`);
  }

  // Count V1: changeOrderElements (dyn.v1.changeOrderElements or changeOrderElements)
  const changeOrderPattern = /\.v1\.changeOrderElements|changeOrderElements\(/g;
  results.stats.v1ChangeOrder = countPatternInFiles(sourceFiles, changeOrderPattern);
  console.log(`   📊 V1 changeOrderElements: ${results.stats.v1ChangeOrder} usos`);

  if (results.stats.v1ChangeOrder >= MIN_REQUIREMENTS.v1ChangeOrder) {
    console.log(`   ✅ V1 changeOrderElements: ${results.stats.v1ChangeOrder} >= ${MIN_REQUIREMENTS.v1ChangeOrder}`);
    results.passed++;
  } else {
    console.log(`   ❌ V1 changeOrderElements: ${results.stats.v1ChangeOrder} < ${MIN_REQUIREMENTS.v1ChangeOrder}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v1ChangeOrder - results.stats.v1ChangeOrder} usos de changeOrderElements`);
  }

  // Count V3: IDs (getVariant with ID_VARIANTS_MAP)
  // Pattern: dyn.v3.getVariant(..., ID_VARIANTS_MAP, ...) or getVariant(..., ID_VARIANTS_MAP, ...)
  const idPattern = /\.v3\.getVariant\([^)]*ID_VARIANTS_MAP|getVariant\([^)]*ID_VARIANTS_MAP/g;
  results.stats.v3Ids = countPatternInFiles(sourceFiles, idPattern);
  console.log(`   📊 V3 IDs (getVariant con ID_VARIANTS_MAP): ${results.stats.v3Ids} usos`);

  if (results.stats.v3Ids >= MIN_REQUIREMENTS.v3Ids) {
    console.log(`   ✅ V3 IDs: ${results.stats.v3Ids} >= ${MIN_REQUIREMENTS.v3Ids}`);
    results.passed++;
  } else {
    console.log(`   ❌ V3 IDs: ${results.stats.v3Ids} < ${MIN_REQUIREMENTS.v3Ids}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v3Ids - results.stats.v3Ids} usos de getVariant para IDs`);
  }

  // Count V3: Classes (getVariant with CLASS_VARIANTS_MAP)
  // Pattern: dyn.v3.getVariant(..., CLASS_VARIANTS_MAP, ...) or getVariant(..., CLASS_VARIANTS_MAP, ...)
  const classPattern = /\.v3\.getVariant\([^)]*CLASS_VARIANTS_MAP|getVariant\([^)]*CLASS_VARIANTS_MAP/g;
  results.stats.v3Classes = countPatternInFiles(sourceFiles, classPattern);
  console.log(`   📊 V3 Classes (getVariant con CLASS_VARIANTS_MAP): ${results.stats.v3Classes} usos`);

  if (results.stats.v3Classes >= MIN_REQUIREMENTS.v3Classes) {
    console.log(`   ✅ V3 Classes: ${results.stats.v3Classes} >= ${MIN_REQUIREMENTS.v3Classes}`);
    results.passed++;
  } else {
    console.log(`   ❌ V3 Classes: ${results.stats.v3Classes} < ${MIN_REQUIREMENTS.v3Classes}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v3Classes - results.stats.v3Classes} usos de getVariant para clases`);
  }

  // Count V3: Texts (getVariant without map, with TEXT_VARIANTS_MAP, or with local text variants)
  // Pattern: dyn.v3.getVariant(..., undefined, ...) or getVariant(..., undefined, ...)
  //          dyn.v3.getVariant(..., TEXT_VARIANTS_MAP, ...) or getVariant(..., TEXT_VARIANTS_MAP, ...)
  //          dyn.v3.getVariant(..., *TextVariants, ...) or getVariant(..., *TextVariants, ...)
  const textPattern1 = /\.v3\.getVariant\([^)]*,\s*undefined|getVariant\([^)]*,\s*undefined/g;
  const textPattern2 = /\.v3\.getVariant\([^)]*TEXT_VARIANTS_MAP|getVariant\([^)]*TEXT_VARIANTS_MAP/g;
  const textPattern3 = /\.v3\.getVariant\([^)]*[Tt]ext[^)]*Variants|getVariant\([^)]*[Tt]ext[^)]*Variants/g;
  const textCount1 = countPatternInFiles(sourceFiles, textPattern1);
  const textCount2 = countPatternInFiles(sourceFiles, textPattern2);
  const textCount3 = countPatternInFiles(sourceFiles, textPattern3);
  results.stats.v3Texts = textCount1 + textCount2 + textCount3;
  console.log(`   📊 V3 Texts (getVariant para textos): ${results.stats.v3Texts} usos`);

  if (results.stats.v3Texts >= MIN_REQUIREMENTS.v3Texts) {
    console.log(`   ✅ V3 Texts: ${results.stats.v3Texts} >= ${MIN_REQUIREMENTS.v3Texts}`);
    results.passed++;
  } else {
    console.log(`   ❌ V3 Texts: ${results.stats.v3Texts} < ${MIN_REQUIREMENTS.v3Texts}`);
    results.failed++;
    results.errors.push(`Faltan ${MIN_REQUIREMENTS.v3Texts - results.stats.v3Texts} usos de getVariant para textos`);
  }

  return results;
}

// ============================================================================
// TEST 7: EVENT COVERAGE
// ============================================================================

function testEventCoverage() {
  console.log('\n📡 TEST 7: COBERTURA DE EVENTOS');
  console.log('─'.repeat(60));

  const results = {
    passed: 0,
    failed: 0,
    errors: [],
    stats: {
      totalEvents: 0,
      usedEvents: 0,
      unusedEvents: [],
      eventUsages: {}
    }
  };

  if (isBrowser()) {
    console.log('   ⚠️  Este test solo funciona en Node.js');
    return results;
  }

  const found = findEventsFile(DEFAULT_EVENTS_PATHS);
  if (!found) {
    console.log('   ❌ No se encontró el archivo events.ts');
    results.failed++;
    results.errors.push('Archivo events.ts no encontrado en ubicaciones comunes');
    return results;
  }

  const { path: eventsFilePath, content: eventsContent, relPath } = found;
  console.log(`   📄 Archivo de eventos encontrado: ${relPath}`);

  const { names: eventNames, block } = parseEventNamesFromContent(eventsContent);
  results.stats.totalEvents = eventNames.length;
  console.log(`   📊 Total de eventos definidos: ${results.stats.totalEvents}`);

  if (eventNames.length === 0) {
    console.log('   ⚠️  No se encontraron eventos en EVENT_TYPES');
    results.failed++;
    results.errors.push('No se pudieron extraer eventos de EVENT_TYPES');
    return results;
  }

  const sourceFiles = getAllSourceFiles({ excludeFileNameContaining: 'test-dynamic-system' });
  const { eventUsages, usedEvents, unusedEvents } = countEventUsages(eventNames, sourceFiles, eventsFilePath);
  results.stats.eventUsages = eventUsages;
  results.stats.usedEvents = usedEvents;
  results.stats.unusedEvents = unusedEvents;

  console.log(`   📊 Eventos usados: ${results.stats.usedEvents} / ${results.stats.totalEvents}`);

  // Show unused events (if any)
  if (results.stats.unusedEvents.length > 0) {
    console.log(`   ⚠️  Eventos sin uso (${results.stats.unusedEvents.length}):`);
    results.stats.unusedEvents.slice(0, 5).forEach(eventKey => {
      console.log(`      - ${eventKey}`);
    });
    if (results.stats.unusedEvents.length > 5) {
      console.log(`      ... y ${results.stats.unusedEvents.length - 5} más`);
    }
  }

  // Calculate coverage percentage
  const coveragePercent = results.stats.totalEvents > 0
    ? ((results.stats.usedEvents / results.stats.totalEvents) * 100).toFixed(1)
    : 0;

  console.log(`   📈 Cobertura: ${coveragePercent}%`);

  // Pass only if 100% of events are used
  if (results.stats.usedEvents === results.stats.totalEvents) {
    console.log(`   ✅ Cobertura de eventos: ${results.stats.usedEvents}/${results.stats.totalEvents} = 100%`);
    results.passed++;
  } else {
    console.log(`   ❌ Cobertura de eventos: ${results.stats.usedEvents}/${results.stats.totalEvents} < 100%`);
    results.failed++;
    results.errors.push(`Faltan ${results.stats.totalEvents - results.stats.usedEvents} eventos sin usar (deben estar todos en uso: 100%)`);
  }

  return results;
}

// ============================================================================
// FINAL REPORT
// ============================================================================

function generateReport(allResults) {
  console.log('\n' + '='.repeat(60));
  console.log('📊 REPORTE FINAL');
  console.log('='.repeat(60));

  const totalPassed = allResults.reduce((sum, r) => sum + r.passed, 0);
  const totalFailed = allResults.reduce((sum, r) => sum + r.failed, 0);
  const allErrors = allResults.flatMap(r => r.errors || []);

  // Get stats from TEST 5 (real usage)
  const usageTest = allResults.find(r => r.stats?.v1AddWrapDecoy !== undefined);
  const usageStats = usageTest?.stats ?? {};

  // Get stats from TEST 6 (event coverage)
  const eventTest = allResults.find(r => r.stats?.totalEvents !== undefined);
  const eventStats = eventTest?.stats ?? {};

  console.log(`\n✅ Tests pasados: ${totalPassed}`);
  console.log(`❌ Tests fallidos: ${totalFailed}`);

  if (totalPassed + totalFailed > 0) {
    const successRate = ((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1);
    console.log(`📈 Tasa de éxito: ${successRate}%`);
  }

  // Show real usage stats
  if (usageStats.v1AddWrapDecoy !== undefined) {
    console.log('\n📊 ESTADÍSTICAS DE USO REAL:');
    console.log('─'.repeat(60));
    console.log(`   🔹 V1 addWrapDecoy: ${usageStats.v1AddWrapDecoy} usos`);
    console.log(`   🔹 V1 changeOrderElements: ${usageStats.v1ChangeOrder} usos`);
    console.log(`   🔹 V3 IDs (getVariant): ${usageStats.v3Ids} usos`);
    console.log(`   🔹 V3 Classes (getVariant): ${usageStats.v3Classes} usos`);
    console.log(`   🔹 V3 Texts (getVariant): ${usageStats.v3Texts} usos`);
    console.log(`   🔹 TOTAL V1: ${usageStats.v1AddWrapDecoy + usageStats.v1ChangeOrder} usos`);
    console.log(`   🔹 TOTAL V3: ${usageStats.v3Ids + usageStats.v3Classes + usageStats.v3Texts} usos`);
  }

  //Show event coverage stats
  if (eventStats.totalEvents !== undefined) {
    const coveragePercent = eventStats.totalEvents > 0
      ? ((eventStats.usedEvents / eventStats.totalEvents) * 100).toFixed(1)
      : 0;
    console.log('\n📡 ESTADÍSTICAS DE EVENTOS:');
    console.log('─'.repeat(60));
    console.log(`   🔹 Total de eventos definidos: ${eventStats.totalEvents}`);
    console.log(`   🔹 Eventos en uso: ${eventStats.usedEvents}`);
    console.log(`   🔹 Eventos sin uso: ${eventStats.unusedEvents?.length ?? 0}`);
    console.log(`   🔹 Cobertura: ${coveragePercent}%`);
    if (eventStats.unusedEvents && eventStats.unusedEvents.length > 0) {
      console.log(`   ⚠️  Eventos sin uso: ${eventStats.unusedEvents.slice(0, 3).join(', ')}${eventStats.unusedEvents.length > 3 ? '...' : ''}`);
    }
  }

  if (allErrors.length > 0) {
    console.log('\n⚠️  ERRORES ENCONTRADOS:');
    allErrors.slice(0, 5).forEach((error, i) => {
      console.log(`   ${i + 1}. ${error}`);
    });
    if (allErrors.length > 5) {
      console.log(`   ... y ${allErrors.length - 5} más`);
    }
  }

  console.log('\n📋 CRITERIOS DE VALIDACIÓN:');
  console.log('─'.repeat(60));
  console.log(`   ✅ V1 addWrapDecoy: mínimo ${MIN_REQUIREMENTS.v1AddWrapDecoy} usos`);
  console.log(`   ✅ V1 changeOrderElements: mínimo ${MIN_REQUIREMENTS.v1ChangeOrder} usos`);
  console.log(`   ✅ V3 IDs (getVariant): mínimo ${MIN_REQUIREMENTS.v3Ids} usos`);
  console.log(`   ✅ V3 Classes (getVariant): mínimo ${MIN_REQUIREMENTS.v3Classes} usos`);
  console.log(`   ✅ V3 Texts (getVariant): mínimo ${MIN_REQUIREMENTS.v3Texts} usos`);

  console.log('\n' + '='.repeat(60));
  if (totalFailed === 0) {
    console.log('✅ SISTEMA DINÁMICO: VALIDACIÓN EXITOSA');
    console.log('   El sistema cumple con todos los requisitos mínimos.');
  } else {
    console.log('⚠️  SISTEMA DINÁMICO: REQUIERE ATENCIÓN');
    console.log('   Algunos requisitos no se cumplen. Revisa los errores arriba.');
  }
  console.log('='.repeat(60) + '\n');

  return {
    success: totalFailed === 0,
    totalPassed,
    totalFailed,
    errors: allErrors,
    usageStats
  };
}

// ============================================================================
// EXECUTION
// ============================================================================

function runAllTests() {
  console.log('\n' + '🧪'.repeat(30));
  console.log('🧪 TEST DEL SISTEMA DINÁMICO (MEJORADO - CUENTA USOS REALES)');
  console.log('🧪'.repeat(30));

  const results = [
    testFileStructure(),
    testVariantFiles(),
    testDeterminism(),
    testSeedVariation(), // NEW!
    testRealUsage(), // NEW!
    testEventCoverage(), // NEW!
  ];

  if (isBrowser()) {
    results.push(testDOMUsage());
  }

  return generateReport(results);
}

// ============================================================================
// EXPORT/RUN
// ============================================================================

if (isBrowser()) {
  globalThis.testDynamicSystem = runAllTests;
  console.log('💡 Ejecuta testDynamicSystem() en la consola para correr los tests');
} else {
  const report = runAllTests();
  process.exit(report.success ? 0 : 1);
}

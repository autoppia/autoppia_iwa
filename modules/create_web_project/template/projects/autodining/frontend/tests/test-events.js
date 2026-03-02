#!/usr/bin/env node
/**
 * 🧪 EVENT COVERAGE TEST
 *
 * This script validates that all events defined in EVENT_TYPES are being used
 * in the codebase. It requires 100% coverage (all events must be used).
 *
 * USAGE:
 *   From Node.js: node tests/test-events.js
 */

const {
  isBrowser,
  findEventsFile,
  parseEventNamesFromContent,
  getAllSourceFiles,
  countEventUsages,
  DEFAULT_EVENTS_PATHS
} = require('./test-helpers.js');

// ============================================================================
// TEST: EVENT COVERAGE
// ============================================================================

function testEventCoverage() {
  console.log('\n' + '📡'.repeat(30));
  console.log('📡 TEST DE COBERTURA DE EVENTOS');
  console.log('📡'.repeat(30));

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
    console.log('\n❌ No se encontró el archivo events.ts');
    console.log('   Buscado en:');
    DEFAULT_EVENTS_PATHS.forEach(p => console.log(`      - ${p}`));
    results.failed++;
    results.errors.push('Archivo events.ts no encontrado en ubicaciones comunes');
    return results;
  }

  const { path: eventsFilePath, content: eventsContent, relPath } = found;
  console.log(`\n📄 Archivo de eventos encontrado: ${relPath}`);

  const { names: eventNames, block } = parseEventNamesFromContent(eventsContent);
  if (!block || eventNames.length === 0) {
    console.log('\n❌ No se pudo extraer EVENT_TYPES del archivo');
    results.failed++;
    results.errors.push('No se encontró EVENT_TYPES en el archivo de eventos');
    return results;
  }

  results.stats.totalEvents = eventNames.length;
  console.log(`\n📊 Total de eventos definidos: ${results.stats.totalEvents}`);

  const sourceFiles = getAllSourceFiles({ excludeFileNameContaining: 'test-' });
  console.log(`📂 Archivos fuente analizados: ${sourceFiles.length}`);

  const { eventUsages, usedEvents, unusedEvents } = countEventUsages(eventNames, sourceFiles, eventsFilePath);
  results.stats.eventUsages = eventUsages;
  results.stats.usedEvents = usedEvents;
  results.stats.unusedEvents = unusedEvents;

  console.log(`\n📊 Eventos usados: ${usedEvents} / ${results.stats.totalEvents}`);

  const coveragePercent = results.stats.totalEvents > 0
    ? ((usedEvents / results.stats.totalEvents) * 100).toFixed(1)
    : 0;
  console.log(`📈 Cobertura: ${coveragePercent}%`);

  if (unusedEvents.length > 0) {
    console.log(`\n⚠️  Eventos sin uso (${unusedEvents.length}):`);
    unusedEvents.forEach(eventKey => {
      const eventInfo = eventNames.find(e => e.key === eventKey);
      console.log(`   ❌ ${eventKey} (${eventInfo ? eventInfo.value : 'N/A'})`);
    });
  }

  if (usedEvents === results.stats.totalEvents) {
    console.log(`\n✅ Cobertura de eventos: ${usedEvents}/${results.stats.totalEvents} = 100%`);
    results.passed++;
  } else {
    console.log(`\n❌ Cobertura de eventos: ${usedEvents}/${results.stats.totalEvents} < 100%`);
    results.failed++;
    results.errors.push(`Faltan ${results.stats.totalEvents - usedEvents} eventos sin usar (deben estar todos en uso: 100%)`);
  }

  return results;
}

// ============================================================================
// REPORT
// ============================================================================

function generateReport(result) {
  console.log('\n' + '='.repeat(60));
  console.log('📊 REPORTE FINAL');
  console.log('='.repeat(60));

  console.log(`\n✅ Tests pasados: ${result.passed}`);
  console.log(`❌ Tests fallidos: ${result.failed}`);

  console.log('\n📡 ESTADÍSTICAS DE EVENTOS:');
  console.log('─'.repeat(60));
  console.log(`   🔹 Total de eventos definidos: ${result.stats.totalEvents}`);
  console.log(`   🔹 Eventos en uso: ${result.stats.usedEvents}`);
  console.log(`   🔹 Eventos sin uso: ${result.stats.unusedEvents.length}`);

  const coveragePercent = result.stats.totalEvents > 0
    ? ((result.stats.usedEvents / result.stats.totalEvents) * 100).toFixed(1)
    : 0;
  console.log(`   🔹 Cobertura: ${coveragePercent}%`);

  if (result.errors.length > 0) {
    console.log('\n⚠️  ERRORES:');
    result.errors.forEach((error, i) => {
      console.log(`   ${i + 1}. ${error}`);
    });
  }

  console.log('\n' + '='.repeat(60));
  if (result.failed === 0) {
    console.log('✅ COBERTURA DE EVENTOS: 100% - VALIDACIÓN EXITOSA');
    console.log('   Todos los eventos están en uso.');
  } else {
    console.log('❌ COBERTURA DE EVENTOS: REQUIERE ATENCIÓN');
    console.log('   Algunos eventos no están siendo utilizados.');
  }
  console.log('='.repeat(60) + '\n');

  return {
    success: result.failed === 0,
    totalPassed: result.passed,
    totalFailed: result.failed,
    errors: result.errors,
    stats: result.stats
  };
}

// ============================================================================
// EXECUTION
// ============================================================================

if (isBrowser()) {
  globalThis.testEvents = () => generateReport(testEventCoverage());
  console.log('💡 Ejecuta testEvents() en la consola para correr el test');
} else {
  const result = testEventCoverage();
  const report = generateReport(result);
  process.exit(report.success ? 0 : 1);
}

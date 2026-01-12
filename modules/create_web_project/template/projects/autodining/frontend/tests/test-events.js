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

// ============================================================================
// UTILITIES
// ============================================================================

function isBrowser() {
  return typeof window !== 'undefined';
}

function readFileContent(filePath) {
  if (isBrowser()) return '';
  const fs = require('fs');
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

function getAllSourceFiles() {
  if (isBrowser()) return [];
  const fs = require('fs');
  const pathModule = require('path');
  const srcDir = pathModule.join(process.cwd(), 'src');

  function walkDir(dir, fileList = []) {
    if (!fs.existsSync(dir)) return fileList;
    const files = fs.readdirSync(dir);
    files.forEach(file => {
      const filePath = pathModule.join(dir, file);
      try {
        const stat = fs.statSync(filePath);
        if (stat.isDirectory() && !filePath.includes('node_modules') && !filePath.includes('.next') && !filePath.includes('__pycache__')) {
          walkDir(filePath, fileList);
        } else if ((file.endsWith('.tsx') || file.endsWith('.ts')) && !file.includes('test-')) {
          fileList.push(filePath);
        }
      } catch (err) {
        // Skip files we can't read
      }
    });
    return fileList;
  }

  if (fs.existsSync(srcDir)) {
    return walkDir(srcDir);
  }
  return [];
}

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

  const fs = require('fs');
  const pathModule = require('path');

  // Try to find events.ts file in common locations
  const possiblePaths = [
    'src/library/events.ts',
    'src/lib/events.ts',
    'src/library/event.ts',
    'src/lib/event.ts'
  ];

  let eventsFilePath = null;
  let eventsContent = '';

  for (const relPath of possiblePaths) {
    const fullPath = pathModule.join(process.cwd(), relPath);
    if (fs.existsSync(fullPath)) {
      eventsFilePath = fullPath;
      eventsContent = readFileContent(fullPath);
      console.log(`\n📄 Archivo de eventos encontrado: ${relPath}`);
      break;
    }
  }

  if (!eventsFilePath) {
    console.log('\n❌ No se encontró el archivo events.ts');
    console.log('   Buscado en:');
    possiblePaths.forEach(p => console.log(`      - ${p}`));
    results.failed++;
    results.errors.push('Archivo events.ts no encontrado en ubicaciones comunes');
    return results;
  }

  // Extract EVENT_TYPES from the file
  const eventTypesMatch = eventsContent.match(/export\s+const\s+EVENT_TYPES\s*=\s*\{([^}]+)\}/s);
  if (!eventTypesMatch) {
    console.log('\n❌ No se pudo extraer EVENT_TYPES del archivo');
    results.failed++;
    results.errors.push('No se encontró EVENT_TYPES en el archivo de eventos');
    return results;
  }

  const eventTypesBlock = eventTypesMatch[1];

  // Extract event names (KEY: "VALUE" or KEY: 'VALUE')
  const eventNamePattern = /(\w+)\s*:\s*["']([^"']+)["']/g;
  const eventNames = [];
  let match;

  while ((match = eventNamePattern.exec(eventTypesBlock)) !== null) {
    const eventKey = match[1];
    const eventValue = match[2];
    eventNames.push({ key: eventKey, value: eventValue });
  }

  // Also try to match commented out events (// EVENT_NAME: "EVENT_NAME")
  const commentedPattern = /\/\/\s*(\w+)\s*:\s*["']([^"']+)["']/g;
  while ((match = commentedPattern.exec(eventTypesBlock)) !== null) {
    const eventKey = match[1];
    const eventValue = match[2];
    // Only add if not already in the list
    if (!eventNames.find(e => e.key === eventKey)) {
      eventNames.push({ key: eventKey, value: eventValue });
    }
  }

  results.stats.totalEvents = eventNames.length;
  console.log(`\n📊 Total de eventos definidos: ${results.stats.totalEvents}`);

  if (eventNames.length === 0) {
    console.log('\n⚠️  No se encontraron eventos en EVENT_TYPES');
    results.failed++;
    results.errors.push('No se pudieron extraer eventos de EVENT_TYPES');
    return results;
  }

  // Get all source files
  const sourceFiles = getAllSourceFiles();
  console.log(`📂 Archivos fuente analizados: ${sourceFiles.length}`);

  // Check usage of each event
  eventNames.forEach(({ key, value }) => {
    // Look for: logEvent(EVENT_TYPES.KEY, ...) or logEvent(EVENT_TYPES['KEY'], ...)
    // Also look for: EVENT_TYPES.KEY or EVENT_TYPES['KEY'] (direct reference)
    const pattern1 = new RegExp(`logEvent\\([^)]*EVENT_TYPES\\.${key}[^)]*\\)`, 'g');
    const pattern2 = new RegExp(`logEvent\\([^)]*EVENT_TYPES\\['${key}'\\][^)]*\\)`, 'g');
    const pattern3 = new RegExp(`EVENT_TYPES\\.${key}`, 'g');
    const pattern4 = new RegExp(`EVENT_TYPES\\['${key}'\\]`, 'g');
    const pattern5 = new RegExp(`["']${value}["']`, 'g'); // Direct string usage

    let usageCount = 0;
    sourceFiles.forEach(file => {
      const content = readFileContent(file);
      // Don't count the events.ts file itself
      if (file === eventsFilePath) return;

      const matches1 = content.match(pattern1);
      const matches2 = content.match(pattern2);
      const matches3 = content.match(pattern3);
      const matches4 = content.match(pattern4);
      const matches5 = content.match(pattern5);

      usageCount += (matches1 ? matches1.length : 0);
      usageCount += (matches2 ? matches2.length : 0);
      // For pattern3 and pattern4, only count if not in events.ts
      if (file !== eventsFilePath) {
        usageCount += (matches3 ? matches3.length : 0);
        usageCount += (matches4 ? matches4.length : 0);
      }
      // For pattern5, be more careful - only count if it's in a logEvent call context
      if (matches5) {
        // Check if it's in a logEvent call
        const logEventContext = content.match(new RegExp(`logEvent\\([^)]*["']${value}["'][^)]*\\)`, 'g'));
        if (logEventContext) {
          usageCount += logEventContext.length;
        }
      }
    });

    results.stats.eventUsages[key] = usageCount;

    if (usageCount > 0) {
      results.stats.usedEvents++;
    } else {
      results.stats.unusedEvents.push(key);
    }
  });

  console.log(`\n📊 Eventos usados: ${results.stats.usedEvents} / ${results.stats.totalEvents}`);

  // Calculate coverage percentage
  const coveragePercent = results.stats.totalEvents > 0
    ? ((results.stats.usedEvents / results.stats.totalEvents) * 100).toFixed(1)
    : 0;

  console.log(`📈 Cobertura: ${coveragePercent}%`);

  // Show unused events (if any)
  if (results.stats.unusedEvents.length > 0) {
    console.log(`\n⚠️  Eventos sin uso (${results.stats.unusedEvents.length}):`);
    results.stats.unusedEvents.forEach(eventKey => {
      const eventInfo = eventNames.find(e => e.key === eventKey);
      console.log(`   ❌ ${eventKey} (${eventInfo ? eventInfo.value : 'N/A'})`);
    });
  }

  // Pass only if 100% of events are used
  if (results.stats.usedEvents === results.stats.totalEvents) {
    console.log(`\n✅ Cobertura de eventos: ${results.stats.usedEvents}/${results.stats.totalEvents} = 100%`);
    results.passed++;
  } else {
    console.log(`\n❌ Cobertura de eventos: ${results.stats.usedEvents}/${results.stats.totalEvents} < 100%`);
    results.failed++;
    results.errors.push(`Faltan ${results.stats.totalEvents - results.stats.usedEvents} eventos sin usar (deben estar todos en uso: 100%)`);
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
  window.testEvents = () => generateReport(testEventCoverage());
  console.log('💡 Ejecuta testEvents() en la consola para correr el test');
} else {
  const result = testEventCoverage();
  const report = generateReport(result);
  process.exit(report.success ? 0 : 1);
}

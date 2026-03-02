#!/usr/bin/env node
/**
 * Shared test utilities for dynamic system and event coverage tests.
 * Reduces duplication between test-dynamic-system.js and test-events.js.
 */

// ---------------------------------------------------------------------------
// Environment & I/O
// ---------------------------------------------------------------------------

function isBrowser() {
  return globalThis.window !== undefined;
}

function readFileContent(filePath) {
  if (isBrowser()) return '';
  const fs = require('node:fs');
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

/**
 * Recursively collect source file paths under src/.
 * @param {Object} options
 * @param {string} [options.excludeFileNameContaining] - Skip files whose path contains this string (e.g. 'test-dynamic-system' or 'test-')
 * @returns {string[]}
 */
function getAllSourceFiles(options = {}) {
  if (isBrowser()) return [];
  const fs = require('node:fs');
  const pathModule = require('node:path');
  const srcDir = pathModule.join(process.cwd(), 'src');
  const exclude = options.excludeFileNameContaining;

  function walkDir(dir, fileList = []) {
    if (!fs.existsSync(dir)) return fileList;
    const files = fs.readdirSync(dir);
    files.forEach(file => {
      const filePath = pathModule.join(dir, file);
      try {
        const stat = fs.statSync(filePath);
        if (stat.isDirectory() && !filePath.includes('node_modules') && !filePath.includes('.next') && !filePath.includes('__pycache__')) {
          walkDir(filePath, fileList);
        } else if ((file.endsWith('.tsx') || file.endsWith('.ts')) && (!exclude || !filePath.includes(exclude))) {
          fileList.push(filePath);
        }
      } catch {
        // Skip files we can't read (permission, symlink, etc.)
      }
    });
    return fileList;
  }

  if (fs.existsSync(srcDir)) {
    return walkDir(srcDir);
  }
  return [];
}

// ---------------------------------------------------------------------------
// Event coverage (shared by test-dynamic-system and test-events)
// ---------------------------------------------------------------------------

const DEFAULT_EVENTS_PATHS = [
  'src/library/events.ts',
  'src/lib/events.ts',
  'src/library/event.ts',
  'src/lib/event.ts'
];

/**
 * Find events file in common locations and return path and content.
 * @param {string[]} [possiblePaths]
 * @returns {{ path: string, content: string } | null}
 */
function findEventsFile(possiblePaths = DEFAULT_EVENTS_PATHS) {
  if (isBrowser()) return null;
  const fs = require('node:fs');
  const pathModule = require('node:path');
  for (const relPath of possiblePaths) {
    const fullPath = pathModule.join(process.cwd(), relPath);
    if (fs.existsSync(fullPath)) {
      return { path: fullPath, content: readFileContent(fullPath), relPath };
    }
  }
  return null;
}

/**
 * Parse event names from EVENT_TYPES block content (key/value pairs and optional commented lines).
 * @param {string} eventsContent - Full file content
 * @returns {{ names: Array<{ key: string, value: string }>, block: string | null }}
 */
function parseEventNamesFromContent(eventsContent) {
  const eventTypesRe = /export\s+const\s+EVENT_TYPES\s*=\s*\{([^}]+)\}/s;
  const match = eventTypesRe.exec(eventsContent);
  if (!match) return { names: [], block: null };
  const eventTypesBlock = match[1];
  const names = [];
  const eventNamePattern = /(\w+)\s*:\s*["']([^"']+)["']/g;
  let m;
  while ((m = eventNamePattern.exec(eventTypesBlock)) !== null) {
    names.push({ key: m[1], value: m[2] });
  }
  const commentedPattern = /\/\/\s*(\w+)\s*:\s*["']([^"']+)["']/g;
  while ((m = commentedPattern.exec(eventTypesBlock)) !== null) {
    if (!names.some(e => e.key === m[1])) {
      names.push({ key: m[1], value: m[2] });
    }
  }
  return { names, block: eventTypesBlock };
}

/**
 * Count usage of each event in source files (excluding the events file).
 * @param {Array<{ key: string, value: string }>} eventNames
 * @param {string[]} sourceFiles
 * @param {string} eventsFilePath - Path to events file (excluded from counting)
 * @returns {{ eventUsages: Object<string, number>, usedEvents: number, unusedEvents: string[] }}
 */
function countEventUsages(eventNames, sourceFiles, eventsFilePath) {
  const eventUsages = {};
  let usedEvents = 0;
  const unusedEvents = [];
  const escapeRe = /[\^$*+?.()|[\]{}]/g;

  eventNames.forEach(({ key, value }) => {
    const pattern1 = new RegExp(String.raw`logEvent\([^)]*EVENT_TYPES\.${key}[^)]*\)`, 'g');
    const pattern2 = new RegExp(String.raw`logEvent\([^)]*EVENT_TYPES\['${key}'\]\s*[^)]*\)`, 'g');
    const pattern3 = new RegExp(String.raw`EVENT_TYPES\.${key}`, 'g');
    const pattern4 = new RegExp(String.raw`EVENT_TYPES\['${key}'\]`, 'g');
    const safeValue = value.replaceAll(escapeRe, String.raw`\$&`);
    const pattern5 = new RegExp(`["']${safeValue}["']`, 'g');

    let usageCount = 0;
    sourceFiles.forEach(file => {
      if (file === eventsFilePath) return;
      const content = readFileContent(file);
      const matches1 = content.match(pattern1);
      const matches2 = content.match(pattern2);
      const matches3 = content.match(pattern3);
      const matches4 = content.match(pattern4);
      const matches5 = content.match(pattern5);
      usageCount += (matches1 ? matches1.length : 0) + (matches2 ? matches2.length : 0);
      usageCount += (matches3 ? matches3.length : 0) + (matches4 ? matches4.length : 0);
      if (matches5) {
        const logEventRe = new RegExp(String.raw`logEvent\([^)]*["']${safeValue}["'][^)]*\)`, 'g');
        let execMatch;
        while ((execMatch = logEventRe.exec(content)) !== null) {
          usageCount += 1;
        }
      }
    });

    eventUsages[key] = usageCount;
    if (usageCount > 0) usedEvents++;
    else unusedEvents.push(key);
  });

  return { eventUsages, usedEvents, unusedEvents };
}

module.exports = {
  isBrowser,
  readFileContent,
  getAllSourceFiles,
  findEventsFile,
  parseEventNamesFromContent,
  countEventUsages,
  DEFAULT_EVENTS_PATHS
};

#!/usr/bin/env bash
# SonarCloud coverage alignment script for autoppia_iwa
# - Verifies coverage.xml paths vs Sonar config
# - Ensures sonar.coverage.exclusions mirror .coveragerc omit
# - Optionally normalizes coverage.xml paths for projectBaseDir=autoppia_iwa
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
# When run from monorepo root, autoppia_iwa is the project subdir
if [[ -d "$REPO_ROOT/autoppia_iwa" && -f "$REPO_ROOT/autoppia_iwa/sonar-project.properties" ]]; then
  PROJECT_DIR="$REPO_ROOT/autoppia_iwa"
  REPO_ROOT_FOR_COVERAGE="$REPO_ROOT"
else
  PROJECT_DIR="$REPO_ROOT"
  REPO_ROOT_FOR_COVERAGE="$REPO_ROOT"
fi

COVERAGE_XML="${COVERAGE_XML:-$REPO_ROOT_FOR_COVERAGE/coverage.xml}"
COVERAGERC="${COVERAGERC:-$PROJECT_DIR/.coveragerc}"
SONAR_PROPS="${SONAR_PROPS:-$PROJECT_DIR/sonar-project.properties}"
OUTPUT_COVERAGE_XML="${OUTPUT_COVERAGE_XML:-}"

log() { echo "[sonar-coverage-fix] $*"; }
warn() { echo "[sonar-coverage-fix] WARN: $*" >&2; }
err()  { echo "[sonar-coverage-fix] ERROR: $*" >&2; }

# --- Checks ---
check_file() {
  if [[ ! -f "$1" ]]; then
    err "Missing file: $1"
    return 1
  fi
  log "Found: $1"
  return 0
}

check_coverage_has_paths() {
  if ! grep -q 'filename=' "$COVERAGE_XML" 2>/dev/null; then
    err "No filename= in $COVERAGE_XML (empty or invalid report)"
    return 1
  fi
  log "Coverage XML contains file entries"
  return 0
}

# Detect path style in coverage.xml (autoppia_iwa/... vs relative to project)
detect_coverage_path_style() {
  local first_path
  first_path=$(grep -oP 'filename="\K[^"]+' "$COVERAGE_XML" 2>/dev/null | head -1)
  if [[ -z "$first_path" ]]; then
    echo "unknown"
    return
  fi
  if [[ "$first_path" == autoppia_iwa/* ]]; then
    echo "prefix_autoppia_iwa"
  else
    echo "relative_to_project"
  fi
}

# Detect Sonar project base: where sonar-project.properties is
get_sonar_project_base() {
  if [[ -f "$SONAR_PROPS" ]]; then
    dirname "$SONAR_PROPS"
  else
    echo "$REPO_ROOT"
  fi
}

# Returns "match" if paths in XML will match Sonar's view; "mismatch" otherwise
check_path_alignment() {
  local style base
  style=$(detect_coverage_path_style)
  base=$(cd "$(get_sonar_project_base)" && pwd)
  local proj_real
  proj_real=$(cd "$PROJECT_DIR" && pwd)

  if [[ "$style" == "prefix_autoppia_iwa" ]]; then
    # Sonar sees files as autoppia_iwa/... only if project base is repo root
    if [[ "$base" == "$REPO_ROOT_FOR_COVERAGE" ]] || [[ "$base" == "$(cd "$REPO_ROOT_FOR_COVERAGE" && pwd)" ]]; then
      log "Path alignment: coverage has autoppia_iwa/ prefix; project base is repo root -> OK"
      echo "match"
    else
      warn "Path alignment: coverage has autoppia_iwa/ prefix but project base is $base. Sonar expects paths relative to base -> MISMATCH"
      echo "mismatch"
    fi
  else
    if [[ "$base" == "$proj_real" ]]; then
      log "Path alignment: coverage paths relative to project; project base is project dir -> OK"
      echo "match"
    else
      warn "Path alignment: coverage is relative but project base may not match -> check manually"
      echo "unknown"
    fi
  fi
}

# Ensure sonar.coverage.exclusions mirrors .coveragerc omit (report only)
check_exclusions() {
  local omit_patterns sonar_line
  if [[ ! -f "$COVERAGERC" ]]; then return 0; fi
  if [[ ! -f "$SONAR_PROPS" ]]; then return 0; fi

  omit_patterns=$(sed -n '/^\[run\]/,/^\[/p' "$COVERAGERC" | sed -n '/^omit/,/^[[:space:]]*$/p' | grep -v '^omit' | grep -v '^$' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || true)
  sonar_line=$(grep -E '^sonar\.coverage\.exclusions' "$SONAR_PROPS" 2>/dev/null | sed 's/.*=//' || true)

  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    # Normalize: strip autoppia_iwa/ for comparison with Sonar **/ patterns
    local norm="${line#autoppia_iwa/}"
    if [[ -n "$sonar_line" ]]; then
      if ! echo "$sonar_line" | grep -qE "$(echo "$norm" | sed 's/\./\\./g;s/\*/.*/g')"; then
        log "Sonar coverage exclusions may be missing pattern for: $line (consider **/${norm})"
      fi
    fi
  done <<< "$omit_patterns"
  log "Exclusions check done (review sonar-project.properties if overall % is low)"
}

# Fix: rewrite coverage.xml so paths are relative to source root (strip autoppia_iwa/)
# SonarCloud Python analyzer expects paths relative to sonar.sources root, not project base.
normalize_coverage_xml_paths() {
  local out_xml
  out_xml="${OUTPUT_COVERAGE_XML:-$COVERAGE_XML}"

  if [[ "$(detect_coverage_path_style)" != "prefix_autoppia_iwa" ]]; then
    log "Coverage paths already relative to source root; no rewrite needed"
    return 0
  fi

  log "Rewriting coverage.xml: strip 'autoppia_iwa/' so paths match Sonar source root (sonar.sources)"
  sed 's|filename="autoppia_iwa/|filename="|g' "$COVERAGE_XML" > "${out_xml}.tmp"
  mv "${out_xml}.tmp" "$out_xml"
  log "Written: $out_xml"
}

# --- Main ---
main() {
  log "REPO_ROOT=$REPO_ROOT_FOR_COVERAGE PROJECT_DIR=$PROJECT_DIR COVERAGE_XML=$COVERAGE_XML"
  fails=0

  check_file "$COVERAGE_XML" || fails=$((fails+1))
  check_file "$SONAR_PROPS"  || fails=$((fails+1))
  check_coverage_has_paths   || fails=$((fails+1))

  if [[ -f "$COVERAGERC" ]]; then
    check_exclusions
  else
    warn ".coveragerc not found at $COVERAGERC"
  fi

  alignment=$(check_path_alignment)
  # Always strip autoppia_iwa/ prefix when present: SonarCloud Python analyzer expects
  # paths relative to sonar.sources root (e.g. config/config.py), not project base.
  if [[ "$(detect_coverage_path_style)" == "prefix_autoppia_iwa" ]]; then
    log "Normalizing coverage paths for Sonar source root (fixes 0%% new code coverage)"
    normalize_coverage_xml_paths
  elif [[ "$alignment" == "mismatch" ]]; then
    log "Fixing path mismatch by normalizing coverage.xml paths"
    normalize_coverage_xml_paths
  fi

  if [[ $fails -gt 0 ]]; then
    err "Some checks failed. Fix the issues above and ensure coverage.xml is generated before SonarCloud."
    exit 1
  fi
  log "Done. Run SonarCloud scan after this step."
}

main "$@"

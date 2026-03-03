#!/usr/bin/env python3
"""
Convert pip-audit JSON output to SARIF 2.1 for SonarCloud import.
Usage: python pip_audit_to_sarif.py < pip-audit.json > output.sarif
       python pip_audit_to_sarif.py pip-audit.json -o output.sarif
"""

import json
import sys
from pathlib import Path


def _parse_vuln(v: dict, name: str, version: str) -> dict:
    vuln_id = v.get("id") or v.get("advisory_id") or v.get("cve") or "unknown"
    desc = v.get("description") or v.get("description_short") or f"Vulnerability {vuln_id}"
    fix_versions = v.get("fix_versions") or v.get("fixed_versions") or v.get("fix_version") or []
    if isinstance(fix_versions, str):
        fix_versions = [fix_versions]
    return {
        "name": name,
        "version": version,
        "vuln_id": vuln_id,
        "description": desc,
        "fix_versions": fix_versions,
    }


def parse_pip_audit_json(data: dict | list) -> list[dict]:
    """Extract (name, version, vuln_id, description, fix_versions) from pip-audit JSON."""
    results = []
    # pip-audit 2.x: dict mapping "pkg==version" -> list of vuln objects
    if isinstance(data, dict):
        for dep_spec, vulns in data.items():
            if not isinstance(vulns, list):
                continue
            parts = str(dep_spec).split("==", 1)
            name = parts[0] if parts else "unknown"
            version = parts[1] if len(parts) > 1 else ""
            for v in vulns:
                if isinstance(v, dict):
                    results.append(_parse_vuln(v, name, version))
        return results
    # fallback: list of deps with "vulns" or "vulnerabilities"
    deps = data if isinstance(data, list) else data.get("dependencies", data.get("vulnerabilities", []))
    if not isinstance(deps, list):
        return results
    for dep in deps:
        name = dep.get("name") or dep.get("package_name") or "unknown"
        version = dep.get("version") or dep.get("installed_version") or ""
        vulns = dep.get("vulns") or dep.get("vulnerabilities") or dep.get("advisories") or []
        for v in vulns:
            if isinstance(v, dict):
                results.append(_parse_vuln(v, name, version))
    return results


def build_sarif(results: list[dict]) -> dict:
    """Build SARIF 2.1 document."""
    rules_seen: dict[str, str] = {}
    sarif_results = []
    for r in results:
        fix_msg = f" Upgrade to {', '.join(r['fix_versions'])}." if r["fix_versions"] else ""
        message = f"{r['name']} {r['version']}: {r['description']}.{fix_msg}"
        rules_seen.setdefault(r["vuln_id"], (r["description"][:200] or r["vuln_id"]))
        sarif_results.append(
            {
                "ruleId": r["vuln_id"],
                "level": "error",
                "message": {"text": message},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": "requirements.txt"},
                            "region": {"startLine": 1},
                        }
                    }
                ],
            }
        )
    rules = [
        {
            "id": vid,
            "shortDescription": {"text": desc},
            "helpUri": f"https://osv.dev/vulnerability/{vid}"
            if vid.startswith("PYSEC")
            else f"https://nvd.nist.gov/vuln/detail/{vid}"
            if vid.startswith("CVE-")
            else f"https://github.com/advisories/{vid}",
        }
        for vid, desc in list(rules_seen.items())[:100]
    ]
    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "pip-audit",
                        "version": "2.10.0",
                        "informationUri": "https://pypi.org/project/pip-audit/",
                        "rules": rules,
                    }
                },
                "results": sarif_results,
            }
        ],
    }


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] != "-":
        path = Path(sys.argv[1])
        out_path = Path(sys.argv[3]) if len(sys.argv) >= 4 and sys.argv[2] == "-o" else None
        raw = path.read_text().strip()
        start = max(raw.find("{"), raw.find("["))
        raw = raw[start:] if start >= 0 else raw
        data = json.loads(raw)
    else:
        out_path = None
        data = json.load(sys.stdin)
    # Unwrap nested dict (e.g. {"dependencies": {"pkg==ver": [...]}})
    if isinstance(data, dict):
        inner = data.get("dependencies", data.get("vulnerabilities", data))
        if isinstance(inner, dict) and inner is not data:
            data = inner
    results = parse_pip_audit_json(data)
    sarif = build_sarif(results)
    out = json.dumps(sarif, indent=2)
    if out_path:
        out_path.write_text(out)
    else:
        print(out)


if __name__ == "__main__":
    main()

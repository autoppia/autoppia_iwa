"""
Fetch Task + TaskSolution + EvaluationResult JSONs from a remote service.

This is a best-effort utility: it expects a REST endpoint exposing runs.
If the endpoint is unavailable or schema differs, the script will log and exit
without failing your environment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_url", required=True, help="Service base URL, e.g. http://localhost:9000")
    parser.add_argument("--token", default=None, help="Bearer token if required")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--out", default="data/raw_runs")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    headers = {}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    url = args.base_url.rstrip("/") + "/runs"
    params = {"limit": args.limit}
    print(f"[fetch] GET {url} params={params}")
    try:
        with httpx.Client(timeout=30.0, headers=headers) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print(f"[fetch] Failed to fetch runs: {e}")
        return

    runs = data if isinstance(data, list) else data.get("runs", [])
    if not runs:
        print("[fetch] No runs returned by the service.")
        return

    saved = 0
    for item in runs:
        run_id = item.get("id") or item.get("run_id") or str(saved)
        path = out_dir / f"run_{run_id}.json"
        try:
            path.write_text(json.dumps(item, ensure_ascii=False, indent=2))
            saved += 1
        except Exception as e:
            print(f"[fetch] Failed to save run {run_id}: {e}")
    print(f"[fetch] Saved {saved} run JSONs under {out_dir}")


if __name__ == "__main__":
    main()

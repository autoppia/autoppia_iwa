"""
Health-check demo websites via their /health endpoint.

Usage:
    python -m autoppia_iwa.entrypoints.check.run
    python -m autoppia_iwa.entrypoints.check.run --project autocinema
    iwa check
"""

import argparse
import asyncio

import aiohttp


def _parse_args():
    parser = argparse.ArgumentParser(prog="iwa check", description="Health-check demo websites")
    parser.add_argument("--project", "-p", type=str, help="Project ID (default: all)")
    return parser.parse_args()


async def _check_health(url: str) -> dict | None:
    """Hit /health on backend, return response dict or None on failure."""
    health_url = url.rstrip("/") + "/health"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session, session.get(health_url) as resp:
            if resp.status == 200:
                return await resp.json()
            return None
    except Exception:
        return None


async def _check_frontend(url: str) -> bool:
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session, session.get(url) as resp:
            return resp.status < 500
    except Exception:
        return False


async def run(project_id: str | None = None):
    from autoppia_iwa.config.env import init_env

    init_env()
    from autoppia_iwa.src.demo_webs.config import demo_web_projects

    if project_id:
        by_id = {p.id: p for p in demo_web_projects}
        if project_id not in by_id:
            raise ValueError(f"Unknown project: {project_id}. Available: {list(by_id.keys())}")
        projects = [by_id[project_id]]
    else:
        projects = demo_web_projects

    print(f"\nChecking {len(projects)} project(s)...\n")
    ok = 0
    for project in projects:
        health = await _check_health(project.backend_url)
        frontend_ok = await _check_frontend(project.frontend_url)

        backend_ok = health is not None
        db_ok = health.get("database_pool_operational", False) if health else False
        version = health.get("version", "?") if health else "?"

        all_ok = backend_ok and db_ok and frontend_ok
        icon = "+" if all_ok else "x"

        status_parts = []
        status_parts.append(f"backend={'ok' if backend_ok else 'FAIL'}")
        status_parts.append(f"db={'ok' if db_ok else 'FAIL'}")
        status_parts.append(f"frontend={'ok' if frontend_ok else 'FAIL'}")
        status_parts.append(f"v{version}")

        print(f"  [{icon}] {project.name:<22} {' '.join(status_parts)}")

        if all_ok:
            ok += 1

    print(f"\n{ok}/{len(projects)} healthy\n")
    return ok == len(projects)


def main():
    args = _parse_args()

    try:
        success = asyncio.run(run(project_id=args.project))
    except ValueError as exc:
        print(str(exc))
        raise SystemExit(1) from exc
    raise SystemExit(0 if success else 1)


if __name__ == "__main__":
    main()

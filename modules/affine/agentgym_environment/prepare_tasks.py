from __future__ import annotations

import asyncio

from loguru import logger

from .config import AffineEnvConfig
from .dataset import AffineTaskDataset


async def _run() -> None:
    config = AffineEnvConfig.load_from_env()
    dataset = AffineTaskDataset(config)
    total = await dataset.initialize()
    logger.success("Prepared %d tasks for projects %s", total, config.project_ids)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()

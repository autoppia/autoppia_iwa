#!/usr/bin/env python3
"""Simple TCP port forwarder used to map demo-web ports when container mappings differ."""

from __future__ import annotations

import argparse
import asyncio
import signal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forward a local port to another host:port")
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, required=True)
    parser.add_argument("--target-host", default="127.0.0.1")
    parser.add_argument("--target-port", type=int, required=True)
    return parser.parse_args()


async def handle_client(local_reader: asyncio.StreamReader, local_writer: asyncio.StreamWriter, target_host: str, target_port: int) -> None:
    try:
        remote_reader, remote_writer = await asyncio.open_connection(target_host, target_port)
    except Exception as exc:  # pragma: no cover
        local_writer.close()
        await local_writer.wait_closed()
        return

    async def pipe(src: asyncio.StreamReader, dst: asyncio.StreamWriter):
        try:
            while True:
                data = await src.read(4096)
                if not data:
                    break
                dst.write(data)
                await dst.drain()
        finally:
            dst.close()

    await asyncio.gather(
        pipe(local_reader, remote_writer),
        pipe(remote_reader, local_writer),
    )


async def main() -> None:
    args = parse_args()
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, args.target_host, args.target_port),
        host=args.listen_host,
        port=args.listen_port,
    )
    stop = asyncio.Future()

    def _stop(*_):
        if not stop.done():
            stop.set_result(None)

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, _stop)

    async with server:
        await stop


if __name__ == "__main__":
    asyncio.run(main())

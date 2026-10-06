import asyncio
import logging
from pathlib import Path

from aiohttp_retry import ExponentialRetry

from shazamio import HTTPClient, Serialize, Shazam

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main() -> None:
    # A client you build is a client you close: `Shazam` closes only the one it
    #  builds itself, so this one gets its own block.
    async with HTTPClient(
        retry_options=ExponentialRetry(
            attempts=12,
            max_timeout=204.8,
            statuses={500, 502, 503, 504, 429},
        ),
    ) as http_client:
        shazam = Shazam(http_client=http_client)

        # pass path
        new_version_path = await shazam.recognize("data/Gloria.ogg")
        serialized_new_path = Serialize.full_track(new_version_path)
        print(serialized_new_path)

        # pass bytes
        song_bytes = await asyncio.to_thread(Path("data/Gloria.ogg").read_bytes)
        new_version_path = await shazam.recognize(song_bytes)
        serialized_new_path = Serialize.full_track(new_version_path)
        print(serialized_new_path)


asyncio.run(main())

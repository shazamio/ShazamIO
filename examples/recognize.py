import asyncio
import logging
from pathlib import Path
from typing import Final

from shazamio import Retry, Shazam

logger = logging.getLogger(__name__)

# Resolved from this file, so the example runs from any directory.
SAMPLE: Final[Path] = Path(__file__).parent / "data" / "Gloria.ogg"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main() -> None:
    async with Shazam(
        middleware=[
            Retry(
                attempts=12,
                max_delay=204.8,
            ),
        ],
    ) as shazam:
        # pass path
        out = await shazam.recognize(SAMPLE)
        print(out)

        # pass bytes
        song_bytes = await asyncio.to_thread(SAMPLE.read_bytes)
        out = await shazam.recognize(song_bytes)
        print(out)


asyncio.run(main())

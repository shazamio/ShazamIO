import asyncio
from pathlib import Path
from typing import Final

from shazamio import Shazam

# Resolved from this file, so the example runs from any directory.
SAMPLE: Final[Path] = Path(__file__).parent / "data" / "Gloria.ogg"


async def main() -> None:
    async with Shazam() as shazam:
        out = await shazam.recognize(SAMPLE)
        if out.track is None:
            return

        video = await shazam.get_youtube_data(link=out.track.youtube_link)
        print(video.uri)  # https://youtu.be/6dYWe1c3OyU?autoplay=1


asyncio.run(main())

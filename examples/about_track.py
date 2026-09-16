import asyncio

from shazamio import Serialize, Shazam


async def main() -> None:
    async with Shazam() as shazam:
        track_id: int = 53982678
        about_track = await shazam.track_about(track_id=track_id)
        serialized = Serialize.track(data=about_track)

        print(about_track)  # dict
        print(serialized)  # pydantic model


asyncio.run(main())

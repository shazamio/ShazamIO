import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()
    track_id = 546891609
    related = await shazam.related_tracks(track_id=track_id, limit=5, start_from=2)
    # ONLY №3, №4 SONG
    print(related)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

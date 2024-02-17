import asyncio
from shazamio import Shazam


async def main():
    # Example: https://www.shazam.com/track/559284007/rampampam

    shazam = Shazam()
    track_id = 559284007
    count = await shazam.listening_counter(track_id=track_id)
    print(count)
    count_many = await shazam.listening_counter_many(track_ids=[559284007, 684678069])
    print(count_many)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())

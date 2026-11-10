import asyncio

from shazamio import Shazam


async def main() -> None:
    async with Shazam() as shazam:
        # With several ids the map is keyed by the ids Shazam stores: `1440650711`
        #  comes back as `6781023657`, so indexing by an id you sent can miss.
        keys = await shazam.track_keys_from_apple_ids([1125281672, 1440650711])

        print(keys)  # {'1125281672': '325127876', '6781023657': '56670613'}

        for track_key in keys.values():
            track = await shazam.track_about(track_id=int(track_key))
            print(track.title)


asyncio.run(main())

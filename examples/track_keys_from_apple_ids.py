import asyncio

from shazamio import Serialize, Shazam


async def main() -> None:
    shazam = Shazam()
    # The map is keyed by the ids Shazam stores: `1440650711` comes back as
    #  `6781023657`, so indexing the result by an id you sent can miss.
    keys = await shazam.track_keys_from_apple_ids([1125281672, 1440650711])

    print(keys)  # {'1125281672': '325127876', '6781023657': '56670613'}

    for track_key in keys.values():
        about_track = await shazam.track_about(track_id=int(track_key))
        print(Serialize.track(data=about_track).title)


asyncio.run(main())

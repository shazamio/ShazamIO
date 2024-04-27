import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks("NL", 100)
    tracks = Serialize.playlists(top_five_track_from_amsterdam)
    print(tracks)

    for track in top_five_track_from_amsterdam["data"]:
        serialized = Serialize.playlist(data=track)
        print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())

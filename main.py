import contextlib

from ShazamIO.api import *
from ShazamIO.converter import Converter, Geo
import asyncio

from ShazamIO.factory import ArtistInfo, TrackInfo
from ShazamIO.misc import factory_artist, factory_track
from ShazamIO.models import Request
from ShazamIO.utils import load_file


async def main():

    # artist_id = 201896832
    # top_three_artist_tracks = await shazam.artist_top_tracks(artist_id=artist_id, count=2)
    # for track in top_three_artist_tracks['tracks']:
    #     print(TrackInfoNormalized(track))

    # track_id = 552406075
    # about_track = await shazam.track_about(track_id=track_id)
    # print(about_track)
    # serialized = factory_track.load(about_track, TrackInfo)
    # print(serialized)

    # top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    # for track in top_five_track_from_amsterdam['tracks']:
    #     print(TrackInfoNormalized(track))

    # moscow_id = await Geo().city_id_from('RU', 'Moscow')
    # top_ten_moscow_tracks = await shazam.top_city_tracks(city_id=moscow_id, count=10)
    # print(top_ten_moscow_tracks)

    # top_rock_in_the_world = await shazam.top_world_genre_tracks(genre=7, count=10)
    # print(top_rock_in_the_world)

    # top_spain_rap = await shazam.top_country_genre_tracks(country='ES', genre=2, count=4)
    # for i in top_spain_rap['tracks']:
    #     print(TrackInfoNormalized(i))

    # track_id = 546891609
    # related = await shazam.related_tracks(track_id=track_id, count=3, start_from=2)  # ONLY №3 SONG
    # print(related)

    #artists = await shazam.search_artist(query='Telly Grave', count=5)
    # artists = {'artists': {'hits': [{'follow': {'followkey': 'A_204854258'}, 'alias': 'telly-grave', 'avatar': {'default': 'https://is3-ssl.mzstatic.com/image/thumb/Music124/v4/74/e2/3d/74e23d41-96e7-4be5-34bc-68134c863835/pr_source.png/800x800bb.jpeg', 'blurred': 'https://is3-ssl.mzstatic.com/image/thumb/Music124/v4/74/e2/3d/74e23d41-96e7-4be5-34bc-68134c863835/pr_source.png/800x800bb.jpeg', 'play': 'https://is3-ssl.mzstatic.com/image/thumb/Music124/v4/74/e2/3d/74e23d41-96e7-4be5-34bc-68134c863835/pr_source.png/800x800bb.jpeg'}, 'verified': False, 'url': 'https://www.shazam.com/artist/204854258/telly-grave', 'actions': [{'name': 'artist:204854258', 'type': 'artist', 'id': '204854258'}], 'id': '204854258', 'name': 'TELLY GRAVE'}]}}
    # #
    # for artist in artists['artists']['hits']:
    #     print(artist)
    #     serialized = factory_artist.load(artist, ArtistInfo)
    #     print(serialized)

    # for artist in artists:
    #     print(ArtistInfoNormalized(artist))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


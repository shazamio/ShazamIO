import asyncio
import pytest

from shazamio import Serialize
from shazamio import Shazam


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop

    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(5))

    loop.close()


@pytest.fixture(scope="session")
def song_response():
    response = {
        "matches": [
            {
                "id": "230272433",
                "offset": 187.4215,
                "timeskew": -0.0001565814,
                "frequencyskew": -0.000080525875
            }
        ],
        "location": {
            "accuracy": 0.01
        },
        "timestamp": 1652380596486,
        "timezone": "Europe/Moscow",
        "track": {
            "layout": "5",
            "type": "MUSIC",
            "key": "47440537",
            "title": "Arrival To Earth",
            "subtitle": "Steve Jablonsky",
            "images": {
                "background": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2/35/67"
                              "/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc.jpg/800x800cc"
                              ".jpg",
                "coverart": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi.akybahch"
                            ".jpg/400x400cc.jpg",
                "coverarthq": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi"
                              ".akybahch.jpg/400x400cc.jpg",
                "joecolor": "b:010417p:aec4d5s:ef9b41t:8c9dafq:bf7c38"
            },
            "share": {
                "subject": "Arrival To Earth - Steve Jablonsky",
                "text": "I used Shazam to discover Arrival To Earth by Steve Jablonsky.",
                "href": "https://www.shazam.com/track/47440537/arrival-to-earth",
                "image": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi.akybahch"
                         ".jpg/400x400cc.jpg",
                "twitter": "I used @Shazam to discover Arrival To Earth by Steve Jablonsky.",
                "html": "https://www.shazam.com/snippets/email-share/47440537?lang=en&country=GB",
                "avatar": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2/35/67"
                          "/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc.jpg/800x800cc.jpg",
                "snapchat": "https://www.shazam.com/partner/sc/track/47440537"
            },
            "hub": {
                "type": "APPLEMUSIC",
                "image": "https://images.shazam.com/static/icons/hub/ios/v5/applemusic_{"
                         "scalefactor}.png",
                "actions": [
                    {
                        "name": "apple",
                        "type": "applemusicplay",
                        "id": "265018693"
                    },
                    {
                        "name": "apple",
                        "type": "uri",
                        "uri": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125"
                               "/v4/9c/1d/ec/9c1dec79-214a-c3a4-846b-87787421dc33"
                               "/mzaf_5388156565692493963.plus.aac.ep.m4a"
                    }
                ],
                "options": [
                    {
                        "caption": "OPEN IN",
                        "actions": [
                            {
                                "name": "hub:applemusic:deeplink",
                                "type": "applemusicopen",
                                "uri":
                                    "https://music.apple.com/gb/album/arrival-to-earth/265018176"
                                    "?i=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid"
                                    "=Apple-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D"
                                    "-3235-3830-44754D6D5973&itscg=30201&app=music&itsct=Shazam_ios"
                            },
                            {
                                "name": "hub:applemusic:deeplink",
                                "type": "uri",
                                "uri":
                                    "https://music.apple.com/gb/album/arrival-to-earth/265018176"
                                    "?i=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid"
                                    "=Apple-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D"
                                    "-3235-3830-44754D6D5973&itscg=30201&app=music&itsct=Shazam_ios"
                            }
                        ],
                        "beacondata": {
                            "type": "open",
                            "providername": "applemusic"
                        },
                        "image": "https://images.shazam.com/static/icons/hub/ios/v5/overflow-open"
                                 "-option_{scalefactor}.png",
                        "type": "open",
                        "listcaption": "Open in Apple Music",
                        "overflowimage":
                            "https://images.shazam.com/static/icons/hub/ios/v5/applemusic"
                            "-overflow_{scalefactor}.png",
                        "colouroverflowimage": False,
                        "providername": "applemusic"
                    },
                    {
                        "caption": "BUY",
                        "actions": [
                            {
                                "type": "uri",
                                "uri":
                                    "https://itunes.apple.com/gb/album/arrival-to-earth/265018176"
                                    "?i=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid"
                                    "=Apple-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D"
                                    "-3235-3830-44754D6D5973&itscg=30201&app=itunes&itsct=Shazam_ios"
                            }
                        ],
                        "beacondata": {
                            "type": "buy",
                            "providername": "itunes"
                        },
                        "image": "https://images.shazam.com/static/icons/hub/ios/v5/itunes"
                                 "-overflow-buy_{scalefactor}.png",
                        "type": "buy",
                        "listcaption": "Buy on iTunes",
                        "overflowimage":
                            "https://images.shazam.com/static/icons/hub/ios/v5/itunes-overflow"
                            "-buy_{scalefactor}.png",
                        "colouroverflowimage": False,
                        "providername": "itunes"
                    }
                ],
                "providers": [
                    {
                        "caption": "Open in Spotify",
                        "images": {
                            "overflow":
                                "https://images.shazam.com/static/icons/hub/ios/v5/spotify"
                                "-overflow_{scalefactor}.png",
                            "default":
                                "https://images.shazam.com/static/icons/hub/ios/v5/spotify_{"
                                "scalefactor}.png"
                        },
                        "actions": [
                            {
                                "name": "hub:spotify:searchdeeplink",
                                "type": "uri",
                                "uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky"
                            }
                        ],
                        "type": "SPOTIFY"
                    },
                    {
                        "caption": "Open in Deezer",
                        "images": {
                            "overflow":
                                "https://images.shazam.com/static/icons/hub/ios/v5/deezer"
                                "-overflow_{scalefactor}.png",
                            "default":
                                "https://images.shazam.com/static/icons/hub/ios/v5/deezer_{"
                                "scalefactor}.png"
                        },
                        "actions": [
                            {
                                "name": "hub:deezer:searchdeeplink",
                                "type": "uri",
                                "uri":
                                    "deezer-query://www.deezer.com/play?query=%7Btrack%3A"
                                    "%27Arrival+To+Earth%27%20artist%3A%27Steve+Jablonsky%27%7D "
                            }
                        ],
                        "type": "DEEZER"
                    }
                ],
                "explicit": False,
                "displayname": "APPLE MUSIC"
            },
            "sections": [
                {
                    "type": "SONG",
                    "metapages": [
                        {
                            "image": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2"
                                     "/35/67/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc"
                                     ".jpg/800x800cc.jpg",
                            "caption": "Steve Jablonsky"
                        },
                        {
                            "image": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi"
                                     ".akybahch.jpg/400x400cc.jpg",
                            "caption": "Arrival To Earth"
                        }
                    ],
                    "tabname": "Song",
                    "metadata": [
                        {
                            "title": "Album",
                            "text": "Transformers: The Score"
                        },
                        {
                            "title": "Label",
                            "text": "Warner Records"
                        },
                        {
                            "title": "Released",
                            "text": "2007"
                        }
                    ]
                },
                {
                    "type": "VIDEO",
                    "tabname": "Video",
                    "youtubeurl": "https://cdn.shazam.com/video/v3/-/GB/iphone/47440537/youtube"
                                  "/video?q=Steve+Jablonsky+%22Arrival+To+Earth%22"
                },
                {
                    "type": "ARTIST",
                    "avatar": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2/35/67"
                              "/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc.jpg/800x800cc"
                              ".jpg",
                    "id": "10194644",
                    "name": "Steve Jablonsky",
                    "verified": False,
                    "url": "https://cdn.shazam.com/digest/v1/en/GB/iphone/artist/10194644"
                           "/recentpost",
                    "actions": [
                        {
                            "type": "artistposts",
                            "id": "10194644"
                        },
                        {
                            "type": "artist",
                            "id": "10194644"
                        }
                    ],
                    "tabname": "Artist",
                    "toptracks": {
                        "url": "https://cdn.shazam.com/shazam/v3/en/GB/iphone/-/tracks"
                               "/artisttoptracks_10194644?startFrom=0&pageSize=20&connected="
                    }
                },
                {
                    "type": "RELATED",
                    "url": "https://cdn.shazam.com/shazam/v3/en/GB/iphone/-/tracks/track"
                           "-similarities-id-47440537?startFrom=0&pageSize=20&connected=",
                    "tabname": "Related"
                }
            ],
            "url": "https://www.shazam.com/track/47440537/arrival-to-earth",
            "artists": [
                {
                    "id": "10194644",
                    "adamid": "21402948"
                }
            ],
            "isrc": "USWB10703613",
            "genres": {
                "primary": "Soundtrack"
            },
            "urlparams": {
                "{tracktitle}": "Arrival+To+Earth",
                "{trackartist}": "Steve+Jablonsky"
            },
            "myshazam": {
                "apple": {
                    "actions": [
                        {
                            "name": "myshazam:apple",
                            "type": "uri",
                            "uri": "https://music.apple.com/gb/album/arrival-to-earth/265018176?i"
                                   "=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid=Apple"
                                   "-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D-3235-3830"
                                   "-44754D6D5973&itscg=30201&app=music&itsct=Shazam_ios"
                        }
                    ]
                }
            },
            "highlightsurls": {
                "artisthighlightsurl":
                    "https://cdn.shazam.com/video/v3/en/GB/iphone/21402948/highlights?affiliate"
                    "=mttnagencyid%3Ds2n%26mttnsiteid%3D125115%26mttn3pid%3DApple-Shazam"
                    "%26mttnsub1%3DShazam_ios%26mttnsub2%3D5348615A-616D-3235-3830-44754D6D5973"
                    "%26itscg%3D30201%26app%3Dmusic%26itsct%3DShazam_ios",
                "relatedhighlightsurl":
                    "https://cdn.shazam.com/video/v3/en/GB/iphone/10194644/artist-similarities-id"
                    "-10194644/relatedhighlights?max_artists=5&affiliate=mttnagencyid%3Ds2n"
                    "%26mttnsiteid%3D125115%26mttn3pid%3DApple-Shazam%26mttnsub1%3DShazam_ios"
                    "%26mttnsub2%3D5348615A-616D-3235-3830-44754D6D5973%26itscg%3D30201%26app"
                    "%3Dmusic%26itsct%3DShazam_ios"
            },
            "relatedtracksurl": "https://cdn.shazam.com/shazam/v3/en/GB/iphone/-/tracks/track"
                                "-similarities-id-47440537?startFrom=0&pageSize=20&connected=",
            "albumadamid": "265018176"
        },
        "tagid": "89A4C33B-58C6-4A50-8475-94032FC34D06"
    }
    yield response


@pytest.mark.asyncio(scope="session")
async def test_recognize_song_bug(song_response: bytes):
    serialize_out = Serialize.full_track(data=song_response)
    assert serialize_out.matches[0].channel is None

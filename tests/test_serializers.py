from typing import Any, Final

from shazamio import Serialize

# The shape Shazam's list endpoints return for a track that has no Spotify
#  provider: `hub.providers` is absent, so every field mapped onto a path
#  through it must fall back to its default instead of failing the load.
_TRACK_WITHOUT_SPOTIFY_PROVIDER: Final[dict[str, Any]] = {
    "key": "47440537",
    "title": "Arrival To Earth",
    "subtitle": "Steve Jablonsky",
    "images": {"coverarthq": "https://images.example/cover.jpg"},
    "hub": {"actions": [{"uri": "a"}, {"uri": "ringtone://example"}]},
}


def test_track_missing_paths_fall_back_to_defaults() -> None:
    track = Serialize.track(_TRACK_WITHOUT_SPOTIFY_PROVIDER)

    # The dump also pins a long-standing quirk on purpose: `shazam_url` is built
    #  from the artist id.
    assert track.model_dump() == {
        "key": 47440537,
        "title": "Arrival To Earth",
        "subtitle": "Steve Jablonsky",
        "artist_id": None,
        "shazam_url": "https://www.shazam.com/track/None",
        "photo_url": "https://images.example/cover.jpg",
        "spotify_uri_query": None,
        "apple_music_url": None,
        "ringtone": "ringtone://example",
        "providers": [],
        "spotify_uri": None,
        "youtube_link": None,
        "sections": [],
    }


def test_sections_resolve_by_type_discriminator() -> None:
    track = Serialize.track(
        {
            "key": "1",
            "title": "t",
            "subtitle": "s",
            "sections": [
                {"type": "SONG", "metapages": [], "tabname": "Song", "metadata": []},
                {"type": "VIDEO", "tabname": "Video", "youtubeurl": "https://youtu.be/x"},
                # The ARTIST entry is the case the discriminator exists for:
                #  structurally it also matches `RelatedSection`.
                {
                    "type": "ARTIST",
                    "id": "10194644",
                    "name": "Steve Jablonsky",
                    "verified": False,
                    "url": "https://related-lookalike.example",
                    "actions": [{"type": "artist", "id": "10194644"}],
                    "tabname": "Artist",
                    "toptracks": {"url": "https://tracks.example/top"},
                },
                {"type": "RELATED", "url": "https://related.example", "tabname": "Related"},
            ],
        },
    )

    section_types = [type(section).__name__ for section in track.sections]
    assert section_types == ["SongSection", "VideoSection", "ArtistSection", "RelatedSection"]


# The shape the `iphone` profile returns: one action per provider, so a mapping
#  onto `actions[1]` reads nothing and leaves the Spotify fields `None`.
_TRACK_WITH_PROVIDERS: Final[dict[str, Any]] = {
    "key": "47440537",
    "title": "Arrival To Earth",
    "subtitle": "Steve Jablonsky",
    "hub": {
        "providers": [
            {
                "caption": "Open in Spotify",
                "type": "SPOTIFY",
                "actions": [
                    {
                        "name": "hub:spotify:searchdeeplink",
                        "type": "uri",
                        "uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
                    },
                ],
            },
            {
                "caption": "Open in Deezer",
                "type": "DEEZER",
                "actions": [
                    {
                        "name": "hub:deezer:searchdeeplink",
                        "type": "uri",
                        "uri": "deezer-query://www.deezer.com/play?query=x",
                    },
                ],
            },
        ],
    },
}


def test_the_spotify_fields_read_the_spotify_provider() -> None:
    track = Serialize.track(_TRACK_WITH_PROVIDERS)

    assert track.model_dump() == {
        "key": 47440537,
        "title": "Arrival To Earth",
        "subtitle": "Steve Jablonsky",
        "artist_id": None,
        "shazam_url": "https://www.shazam.com/track/None",
        "photo_url": None,
        "spotify_uri_query": "Arrival%20To%20Earth%20Steve%20Jablonsky",
        "apple_music_url": None,
        "ringtone": None,
        "providers": [
            {
                "caption": "Open in Spotify",
                "type": "SPOTIFY",
                "actions": [
                    {
                        "name": "hub:spotify:searchdeeplink",
                        "type": "uri",
                        "uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
                    },
                ],
            },
            {
                "caption": "Open in Deezer",
                "type": "DEEZER",
                "actions": [
                    {
                        "name": "hub:deezer:searchdeeplink",
                        "type": "uri",
                        "uri": "deezer-query://www.deezer.com/play?query=x",
                    },
                ],
            },
        ],
        "spotify_uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
        "youtube_link": None,
        "sections": [],
    }

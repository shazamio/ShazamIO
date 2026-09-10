from typing import Any, Final

from shazamio import Serialize
from shazamio.schemas.artists import ArtistInfo, ArtistV2

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

    # The dump also pins two long-standing quirks on purpose: `shazam_url` is
    #  built from the artist id, and a payload without `hub.options` yields
    #  `apple_music_url = b""`.
    assert track.model_dump() == {
        "key": 47440537,
        "title": "Arrival To Earth",
        "subtitle": "Steve Jablonsky",
        "artist_id": None,
        "shazam_url": "https://www.shazam.com/track/None",
        "photo_url": "https://images.example/cover.jpg",
        "spotify_uri_query": None,
        "apple_music_url": b"",
        "ringtone": "ringtone://example",
        "spotify_url": None,
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


def test_artist_union_resolves_flat_and_wrapped_payloads() -> None:
    flat: dict[str, Any] = {
        "name": "Steve Jablonsky",
        "verified": False,
        "adamid": "21402948",
        "genres": {"secondaries": ["Soundtrack"], "primary": "Soundtrack"},
        "weburl": "https://www.shazam.com/artist/10194644",
    }
    expected_artist: dict[str, Any] = {
        "name": "Steve Jablonsky",
        "verified": False,
        "genres": ["Soundtrack"],
        "alias": None,
        "genres_primary": "Soundtrack",
        "avatar": None,
        "adam_id": 21402948,
        "url": "https://www.shazam.com/artist/10194644",
    }

    artist = Serialize.artist(flat)

    assert isinstance(artist, ArtistInfo)
    assert artist.model_dump() == expected_artist

    wrapped = Serialize.artist({"artist": flat})

    assert isinstance(wrapped, ArtistV2)
    assert wrapped.artist.model_dump() == expected_artist

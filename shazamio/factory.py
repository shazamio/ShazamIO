from dataclass_factory import Schema


class FactorySchemas:
    FACTORY_TRACK_SCHEMA = Schema(
        name_mapping={
            "photo_url": ("images", "coverarthq"),
            "ringtone": ("hub", "actions", 1, "uri"),
            "artist_id": ("artists", 0, "id"),
            "apple_music_url": ("hub", "options", 0, "actions", 0, "uri"),
            "spotify_url": ("hub", "providers", 0, "actions", 0, "uri"),
            "spotify_uri": ("hub", "providers", 0, "actions", 1, "uri"),
            "sections": "sections",
        },
        skip_internal=True,
    )

    FACTORY_ARTIST_SCHEMA = Schema(
        name_mapping={
            "avatar": "avatar",
            "genres": ("genres", "secondaries"),
            "genres_primary": ("genres", "primary"),
            "adam_id": "adamid",
            "url": "weburl",
        }
    )

    FACTORY_SONG_SECTION_SCHEMA = Schema(
        name_mapping={
            "type": "type",
            "meta_pages": "metapages",
            "tab_name": "tabname",
            "metadata": "metadata",
        },
        skip_internal=True,
    )

    FACTORY_VIDEO_SECTION_SCHEMA = Schema(
        name_mapping={
            "type": "type",
            "youtube_url": "youtubeurl",
            "tab_name": "tabname",
        },
        skip_internal=True,
    )

    FACTORY_RELATED_SECTION_SCHEMA = Schema(
        name_mapping={
            "type": "type",
            "url": "url",
            "tab_name": "tabname",
        },
        skip_internal=True,
    )

    FACTORY_YOUTUBE_TRACK_SCHEMA = Schema(
        name_mapping={
            "caption": "caption",
            "image": "image",
            "actions": "actions",
        },
        skip_internal=True,
    )

    FACTORY_RESPONSE_TRACK_SCHEMA = Schema(
        name_mapping={
            "matches": "matches",
            "location": "location",
            "retry_ms": "retryms",
            "timestamp": "timestamp",
            "timezone": "timezone",
            "track": "track",
            "tag_id": "tagid",
        },
        skip_internal=True,
    )

    FACTORY_LYRICS_SECTION = Schema(
        name_mapping={
            "type": "type",
            "text": "text",
            "footer": "footer",
            "tab_name": "tabname",
            "beacon_data": "beacondata",
        },
    )

    FACTORY_BEACON_DATA_LYRICS_SECTION = Schema(
        name_mapping={
            "lyrics_id": "lyricsid",
            "provider_name": "providername",
            "common_track_id": "commontrackid",
        }
    )

    FACTORY_ARTIST_SECTION = Schema(
        name_mapping={
            "type": "type",
            "id": "id",
            "name": "name",
            "verified": "verified",
            "actions": "actions",
            "tab_name": "tabname",
            "top_tracks": "toptracks",
        }
    )

    FACTORY_MATCH = Schema(
        name_mapping={
            "id": "id",
            "offset": "offset",
            "channel": "channel",
            "time_skew": "timeskew",
            "frequency_skew": "frequencyskew",
        }
    )

    FACTORY_ATTRIBUTES_ARTIST = Schema(
        name_mapping={
            "name": "name",
            "url": "url",
            "artist_bio": "artistBio",
            "genre_names": "genreNames",
        }
    )

    FACTORY_ARTIST_V2 = Schema(
        name_mapping={
            "id": "id",
            "type": "type",
            "attributes": "attributes",
        }
    )

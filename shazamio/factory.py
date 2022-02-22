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
            "_sections": "sections"

        }, skip_internal=True)

    FACTORY_ARTIST_SCHEMA = Schema(
        name_mapping={
            "avatar": "avatar",
            "genres": ("genres", "secondaries"),
            "genres_primary": ("genres", "primary"),
        })

    FACTORY_SONG_SECTION_SCHEMA = Schema(
        name_mapping={
            "type": "type",
            "meta_pages": "metapages",
            "tab_name": "tabname",
            "metadata": "metadata"
        },
        skip_internal=True
    )

    FACTORY_VIDEO_SECTION_SCHEMA = Schema(
        name_mapping={
            "type": "type",
            "youtube_url": "youtubeurl",
            "tab_name": "tabname",
        },
        skip_internal=True
    )

    FACTORY_RELATED_SECTION_SCHEMA = Schema(
        name_mapping={
            "type": "type",
            "url": "url",
            "tab_name": "tabname",
        },
        skip_internal=True
    )

    FACTORY_YOUTUBE_TRACK_SCHEMA = Schema(
        name_mapping={
            "caption": "caption",
            "image": "image",
            "actions": "actions",
        },
        skip_internal=True
    )

    FACTORY_RESPONSE_TRACK_SCHEMA = Schema(
        name_mapping={
            "matches": "matches",
            "location": "location",
            "timestamp": "timestamp",
            "timezone": "timezone",
            "track": "track",
            "tag_id": "tagid",
        },
        skip_internal=True
    )

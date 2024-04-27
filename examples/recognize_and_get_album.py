import asyncio
import logging

from aiohttp_retry import ExponentialRetry

from shazamio import Shazam, Serialize, HTTPClient

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main():
    shazam = Shazam(
        http_client=HTTPClient(
            retry_options=ExponentialRetry(
                attempts=12, max_timeout=204.8, statuses={500, 502, 503, 504, 429}
            ),
        ),
    )

    new_version_path = await shazam.recognize("data/Gloria.ogg")

    album_info = await shazam.search_album(album_id=new_version_path["track"]["albumadamid"])
    album_serialized = Serialize.album_info(data=album_info)
    # Get album name
    print(album_serialized.data[0].attributes.name)

    # And get all tracks in album
    for i in album_serialized.data[0].relationships.tracks.data:
        msg = (
            f"{i.id} | {i.attributes.album_name} | {i.attributes.artist_name} [{i.attributes.name}]"
        )
        print(msg)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())

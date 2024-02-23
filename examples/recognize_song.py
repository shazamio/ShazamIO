import asyncio
import logging

from shazamio import Shazam, Serialize

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main():
    shazam = Shazam()

    # pass path (deprecated)
    old_version = await shazam.recognize_song(data="data/dora.ogg")  # deprecated
    serialized_old = Serialize.full_track(old_version)
    print(serialized_old)

    # pass path
    new_version_path = await shazam.recognize("data/dora.ogg")
    serialized_new_path = Serialize.full_track(new_version_path)
    print(serialized_new_path)

    # pass bytes
    with open("data/dora.ogg", "rb") as file:
        new_version_path = await shazam.recognize(file.read())
        serialized_new_path = Serialize.full_track(new_version_path)
        print(serialized_new_path)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())

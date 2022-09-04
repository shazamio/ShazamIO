<p align="center">
<img src="https://img.shields.io/lgtm/grade/python/github/dotX12/waio" alt="https://img.shields.io/lgtm/grade/python/github/dotX12/waio">
<img src="https://scrutinizer-ci.com/g/dotX12/ShazamIO/badges/quality-score.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/ShazamIO/">
<img src="https://scrutinizer-ci.com/g/dotX12/ShazamIO/badges/code-intelligence.svg?b=master" alt="https://scrutinizer-ci.com/g/dotX12/ShazamIO/">
<img src="https://scrutinizer-ci.com/g/dotX12/ShazamIO/badges/build.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/ShazamIO/">
<img src="https://badge.fury.io/py/shazamio.svg" alt="https://badge.fury.io/py/shazamio">
<img src="https://pepy.tech/badge/shazamio" alt="https://pepy.tech/project/shazamio">
<img src="https://pepy.tech/badge/shazamio/month" alt="https://pepy.tech/project/shazamio">
<img src="https://img.shields.io/github/license/dotX12/shazamio.svg" alt="https://github.com/dotX12/ShazamIO/blob/master/LICENSE.txt">
<br><br>
  
  <img width="1000" src="https://user-images.githubusercontent.com/64792903/109359596-ca561a00-7896-11eb-9c93-9cf1f283b1a5.png">
  🎵 Is a FREE asynchronous library from reverse engineered Shazam API written in Python 3.8+ with asyncio and aiohttp. Includes all the methods that Shazam has, including searching for a song by file.
 
-----
</p>

## 💿 Installation

```
💲 pip install shazamio
```

## 💻 Example


<details> 
<summary>
<i>🔎🎵 Recognize track</i>
</summary>

Recognize a track based on a file<br>

  ```python3
import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()
    out = await shazam.recognize_song('dora.ogg')
    print(out)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>👨‍🎤 About artist</i>
</summary>

Retrieving information from an artist profile<br>
<a href="https://www.shazam.com/artist/43328183/nathan-evans">https://www.shazam.com/artist/43328183/nathan-evans</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    artist_id = 43328183
    about_artist = await shazam.artist_about(artist_id)
    serialized = Serialize.artist(about_artist)

    print(about_artist)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>


<details> 
<summary>
<i>🎵📄 About track</i>
</summary>

Get track information<br>
<a href="https://www.shazam.com/track/552406075/ale-jazz">https://www.shazam.com/track/552406075/ale-jazz</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    track_id = 552406075
    about_track = await shazam.track_about(track_id=track_id)
    serialized = Serialize.track(data=about_track)

    print(about_track)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>🎵⌛ Track listenings count</i>
</summary>

Returns the number of times a particular song has been played<br>
<a href="https://www.shazam.com/track/559284007/rampampam">https://www.shazam.com/track/559284007/rampampam</a>

  ```python3
import asyncio
from shazamio import Shazam


async def main():
    # Example: https://www.shazam.com/track/559284007/rampampam

    shazam = Shazam()
    track_id = 559284007
    count = await shazam.listening_counter(track_id=track_id)
    print(count)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>🎶💬 Similar songs</i>
</summary>

Similar songs based song id<br>
<a href="https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix">https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix</a>

  ```python3
import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()
    track_id = 546891609
    related = await shazam.related_tracks(track_id=track_id, limit=5, start_from=2)
    # ONLY №3, №4 SONG
    print(related)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>🔎👨‍🎤 Search artists</i>
</summary>

Search all artists by prefix<br>
  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    artists = await shazam.search_artist(query='Lil', limit=5)
    for artist in artists['artists']['hits']:
        serialized = Serialize.artist(data=artist)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

  ```
</details>

<details> 
<summary>
<i>🔎🎶 Search tracks</i>
</summary>

Search all tracks by prefix<br>

  ```python3
import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()
    tracks = await shazam.search_track(query='Lil', limit=5)
    print(tracks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

  ```
</details>

<details> 
<summary>
<i>🔝🎶👨‍🎤 Top artist tracks</i>
</summary>

Get the top songs according to Shazam<br>
<a href="https://www.shazam.com/artist/201896832/kizaru">https://www.shazam.com/artist/201896832/kizaru</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    artist_id = 201896832
    top_three_artist_tracks = await shazam.artist_top_tracks(artist_id=artist_id, limit=3)
    for track in top_three_artist_tracks['tracks']:
        serialized_track = Serialize.track(data=track)
        print(serialized_track)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

  ```
</details>

<details> 
<summary>
<i>🔝🎶🏙️ Top tracks in city</i>
</summary>

Retrieving information from an artist profile<br>
<a href="https://www.shazam.com/charts/top-50/russia/moscow">https://www.shazam.com/charts/top-50/russia/moscow</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_ten_moscow_tracks = await shazam.top_city_tracks(country_code='RU', city_name='Moscow', limit=10)
    print(top_ten_moscow_tracks)
    # ALL TRACKS DICT
    for track in top_ten_moscow_tracks['tracks']:
        serialized = Serialize.track(data=track)
        # SERIALIZE FROM DATACLASS FACTORY
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

  ```
</details>

<details> 
<summary>
<i>🔝🎶🏳️‍🌈 Top tracks in country</i>
</summary>

Get the best tracks by country code<br>
<a href="https://www.shazam.com/charts/discovery/netherlands">https://www.shazam.com/charts/discovery/netherlands</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    for track in top_five_track_from_amsterdam['tracks']:
        serialized = Serialize.track(data=track)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>🔝🎶🏳️‍🌈🎸 Top tracks in country by genre</i>
</summary>

The best tracks by a genre in the country<br>
<a href="https://www.shazam.com/charts/genre/spain/hip-hop-rap">https://www.shazam.com/charts/genre/spain/hip-hop-rap</a>

  ```python3
import asyncio
from shazamio import Shazam, GenreMusic


async def main():
    shazam = Shazam()
    top_spain_rap = await shazam.top_country_genre_tracks(
        country_code='ES',
        genre=GenreMusic.HIP_HOP_RAP,
        limit=4
    )
    print(top_spain_rap)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>🔝🎶🌏🎸 Top tracks in word by genre</i>
</summary>

Get world tracks by certain genre<br>
<a href="https://www.shazam.com/charts/genre/world/rock">https://www.shazam.com/charts/genre/world/rock</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize, GenreMusic


async def main():
    shazam = Shazam()
    top_rock_in_the_world = await shazam.top_world_genre_tracks(genre=GenreMusic.ROCK, limit=10)

    for track in top_rock_in_the_world['tracks']:
        serialized_track = Serialize.track(data=track)
        print(serialized_track.spotify_url)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>🔝🎶🌏Top tracks in word</i>
</summary>

Get the best tracks from all over the world<br>
<a href="https://www.shazam.com/charts/top-200/world">https://www.shazam.com/charts/top-200/world</a>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_world_tracks = await shazam.top_world_tracks(limit=10)
    print(top_world_tracks)
    for track in top_world_tracks['tracks']:
        serialized = Serialize.track(track)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>


## How to use data serialization

<details> 
<summary>
<i>Open Code</i>
</summary>

  ```python3
import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    for track in top_five_track_from_amsterdam['tracks']:
        serialized = Serialize.track(data=track)
        print(serialized.title)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<i>Open photo: What song information looks like (Dict)</i>
</summary>
<img src="https://user-images.githubusercontent.com/64792903/109454521-75b4c980-7a65-11eb-917e-62da3abefb8a.png">

</details>

<details> 
<summary>
<i>Open photo: what song information looks like (Custom serializer)</i>
</summary>
<img src="https://user-images.githubusercontent.com/64792903/109454465-57e76480-7a65-11eb-956c-1bcac41d7de5.png">

</details>

Agree, thanks to the serializer, you no longer need to manually select the necessary data from the dictionary. Now the serializer contains the most necessary information about an artist or a track.

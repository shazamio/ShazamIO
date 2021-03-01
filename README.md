<p align="center">
  <img width="1000" src="https://user-images.githubusercontent.com/64792903/109359596-ca561a00-7896-11eb-9c93-9cf1f283b1a5.png">
</p>

----

## 💿 Installation

```
💲 pip install shazamio
```

## How to use data serialization

<details> 
<summary>
<i>Open Code</i>
</summary>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    for track in top_five_track_from_amsterdam['tracks']:
        serialized = FactoryTrack(data=track).serializer()
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

You can get information on a specific attribute like this:

<details> 
<summary>
<i>Open photo: Using an attribute with a Serializer</i>
</summary>
<img src="https://user-images.githubusercontent.com/64792903/109455344-75b5c900-7a67-11eb-9863-a5ecd2859119.png">

</details>

## 💻 Example


<details> 
<summary>
<b>🔎🎵 Recognize track</b>
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
<b>👨‍🎤 About artist</b>
</summary>

Retrieving information from an artist profile<br>
<a href="https://www.shazam.com/artist/43328183/nathan-evans">https://www.shazam.com/artist/43328183/nathan-evans</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryArtist


async def main():
    shazam = Shazam()
    artist_id = 43328183
    about_artist = await shazam.artist_about(artist_id)
    serialized = FactoryArtist(data=about_artist).serializer()

    print(about_artist)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

  ```
</details>


<details> 
<summary>
<b>🎵📄 About track</b>
</summary>

Get track information<br>
<a href="https://www.shazam.com/track/552406075/ale-jazz">https://www.shazam.com/track/552406075/ale-jazz</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    track_id = 552406075
    about_track = await shazam.track_about(track_id=track_id)
    serialized = FactoryTrack(data=about_track).serializer()

    print(about_track)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<b>🎶💬 Similar songs</b>
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
<b>🔎👨‍🎤 Search artists</b>
</summary>

Search all artists by prefix<br>
  ```python3
import asyncio
from shazamio import Shazam, FactoryArtist


async def main():
    shazam = Shazam()
    artists = await shazam.search_artist(query='Lil', limit=5)
    for artist in artists['artists']['hits']:
        serialized = FactoryArtist(artist).serializer()
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<b>🔎🎶 Search tracks</b>
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
<b>🔝🎶👨‍🎤 Top artist tracks</b>
</summary>

Get the top songs according to Shazam<br>
<a href="https://www.shazam.com/artist/201896832/kizaru">https://www.shazam.com/artist/201896832/kizaru</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    artist_id = 201896832
    top_three_artist_tracks = await shazam.artist_top_tracks(artist_id=artist_id, limit=3)
    for track in top_three_artist_tracks['tracks']:
        serialized_track = FactoryTrack(data=track).serializer()
        print(serialized_track)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

  ```
</details>

<details> 
<summary>
<b>🔝🎶🏙️ Top tracks in city</b>
</summary>

Retrieving information from an artist profile<br>
<a href="https://www.shazam.com/charts/top-50/russia/moscow">https://www.shazam.com/charts/top-50/russia/moscow</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    top_ten_moscow_tracks = await shazam.top_city_tracks(country_code='RU',
                                                         city_name='Moscow',
                                                         limit=10)
    print(top_ten_moscow_tracks)
    # ALL TRACKS DICT
    for track in top_ten_moscow_tracks['tracks']:
        serialized = FactoryTrack(track).serializer()
        # SERIALIZE FROM DATACLASS FACTORY
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<b>🔝🎶🏳️‍🌈 Top tracks in country</b>
</summary>

Get the best tracks by country code<br>
<a href="https://www.shazam.com/charts/discovery/netherlands">https://www.shazam.com/charts/discovery/netherlands</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    for track in top_five_track_from_amsterdam['tracks']:
        serialized = FactoryTrack(data=track).serializer()
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<b>🔝🎶🏳️‍🌈🎸 Top tracks in country by genre</b>
</summary>

The best tracks by a genre in the country<br>
<a href="https://www.shazam.com/charts/genre/spain/hip-hop-rap">https://www.shazam.com/charts/genre/spain/hip-hop-rap</a>

  ```python3
import asyncio
from shazamio import Shazam, GenreMusic


async def main():
    shazam = Shazam()
    top_spain_rap = await shazam.top_country_genre_tracks(country='ES',
                                                          genre=GenreMusic.HIP_HOP_RAP,
                                                          limit=4)
    print(top_spain_rap)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

<details> 
<summary>
<b>🔝🎶🌏🎸 Top tracks in word by genre</b>
</summary>

Get world tracks by certain genre<br>
<a href="https://www.shazam.com/charts/genre/world/rock">https://www.shazam.com/charts/genre/world/rock</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack, GenreMusic


async def main():
    shazam = Shazam()
    top_rock_in_the_world = await shazam.top_world_genre_tracks(genre=GenreMusic.ROCK, limit=10)

    for track in top_rock_in_the_world['tracks']:
        serialized_track = FactoryTrack(track).serializer()
        print(serialized_track.spotify_url)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())


  ```
</details>

<details> 
<summary>
<b>🔝🎶🌏Top tracks in word</b>
</summary>

Get the best tracks from all over the world<br>
<a href="https://www.shazam.com/charts/top-200/world">https://www.shazam.com/charts/top-200/world</a>

  ```python3
import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    top_world_tracks = await shazam.top_world_tracks(limit=10)
    print(top_world_tracks)
    for track in top_world_tracks['tracks']:
        serialized = FactoryTrack(track).serializer()
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
  ```
</details>

---


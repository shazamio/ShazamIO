<p align="center">
<img src="https://scrutinizer-ci.com/g/dotX12/ShazamIO/badges/quality-score.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/ShazamIO/">
<img src="https://scrutinizer-ci.com/g/dotX12/ShazamIO/badges/code-intelligence.svg?b=master" alt="https://scrutinizer-ci.com/g/dotX12/ShazamIO/">
<img src="https://scrutinizer-ci.com/g/dotX12/ShazamIO/badges/build.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/ShazamIO/">
<img src="https://badge.fury.io/py/shazamio.svg" alt="https://badge.fury.io/py/shazamio">
<img src="https://pepy.tech/badge/shazamio" alt="https://pepy.tech/project/shazamio">
<img src="https://pepy.tech/badge/shazamio/month" alt="https://pepy.tech/project/shazamio">
<img src="https://img.shields.io/github/license/dotX12/shazamio.svg" alt="https://github.com/dotX12/ShazamIO/blob/master/LICENSE.txt">
<br><br>

  <img width="1000" src="https://user-images.githubusercontent.com/64792903/109359596-ca561a00-7896-11eb-9c93-9cf1f283b1a5.png">
  🎵 Is a FREE asynchronous library from reverse engineered Shazam API written in Python 3.10+ with asyncio and aiohttp. Recognizes a song from a file or from bytes, reads a track and the tracks related to it, and returns every chart Shazam publishes.

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

Recognize a track from a file, a `pathlib.Path`, or the bytes of one. The
sample below ships with the repository, in `examples/data/`<br>

  ```python3
  import asyncio
  from shazamio import Serialize, Shazam


  async def main():
      shazam = Shazam()
      out = await shazam.recognize("Gloria.ogg")

      print(out)  # dict
      print(Serialize.full_track(out).track.title)  # I Will Survive


  asyncio.run(main())
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
  from shazamio import Serialize, Shazam


  async def main():
      shazam = Shazam()
      about_track = await shazam.track_about(track_id=552406075)

      print(about_track)  # dict
      print(Serialize.track(data=about_track))  # pydantic model


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🎶💬 Similar songs</i>
</summary>

Similar songs based on a song id<br>
<a href="https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix">https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix</a>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      shazam = Shazam()
      related = await shazam.related_tracks(track_id=546891609, limit=5, offset=2)
      print(related)


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🍎🔑 Apple Music ids to Shazam track keys</i>
</summary>

Resolve Apple Music track ids to the Shazam track keys `track_about` takes, in
one request. The map comes back keyed by the ids Shazam stores rather than the
ones you sent, so read its values: an id can come back under a different one,
ids of the same recording collapse into one entry, and an id Shazam has no
track for is absent.<br>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      shazam = Shazam()
      keys = await shazam.track_keys_from_apple_ids([1125281672, 1440650711])

      print(keys)  # {'1125281672': '325127876', '6781023657': '56670613'}


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔝🎶🌏 Top tracks in world</i>
</summary>

The 200 most shazamed tracks worldwide<br>
<a href="https://www.shazam.com/charts/top-200/world">https://www.shazam.com/charts/top-200/world</a>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      shazam = Shazam()
      tracks = await shazam.top_world_tracks(limit=10)

      for track in tracks:
          print(f"{track.rank}. {track.artist} - {track.title}")


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔝🎶🏳️ Top tracks in country</i>
</summary>

The 200 most shazamed tracks in a country<br>
<a href="https://www.shazam.com/charts/top-200/netherlands">https://www.shazam.com/charts/top-200/netherlands</a>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      shazam = Shazam()
      tracks = await shazam.top_country_tracks(
          country_code="NL",
          limit=5,
      )

      for track in tracks:
          print(f"{track.rank}. {track.artist} - {track.title}")


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔝🎶🏙️ Top tracks in city</i>
</summary>

The 50 most shazamed tracks in a city. The city name is the one
`services/charts/locations` publishes<br>
<a href="https://www.shazam.com/charts/top-50/russia/moscow">https://www.shazam.com/charts/top-50/russia/moscow</a>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      shazam = Shazam()
      tracks = await shazam.top_city_tracks(
          country_code="RU",
          city_name="Moscow",
          limit=10,
      )

      for track in tracks:
          print(f"{track.rank}. {track.artist} - {track.title}")


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔝🎶🌏🎸 Top tracks in world by genre</i>
</summary>

The most shazamed tracks worldwide in one genre<br>
<a href="https://www.shazam.com/charts/genre/world/rock">https://www.shazam.com/charts/genre/world/rock</a>

  ```python3
  import asyncio
  from shazamio import GenreMusic, Shazam


  async def main():
      shazam = Shazam()
      tracks = await shazam.top_world_genre_tracks(
          genre=GenreMusic.ROCK,
          limit=10,
      )

      for track in tracks:
          print(f"{track.rank}. {track.artist} - {track.title}")


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔝🎶🏳️🎸 Top tracks in country by genre</i>
</summary>

The most shazamed tracks in a country in one genre. Shazam offers only a
handful of genres per country, and asking for one it does not offer answers
`404`, which surfaces as `aiohttp.ClientResponseError`<br>
<a href="https://www.shazam.com/charts/genre/spain/hip-hop-rap">https://www.shazam.com/charts/genre/spain/hip-hop-rap</a>

  ```python3
  import asyncio
  from shazamio import GenreMusic, Shazam


  async def main():
      shazam = Shazam()
      tracks = await shazam.top_country_genre_tracks(
          country_code="ES",
          genre=GenreMusic.HIP_HOP_RAP,
          limit=4,
      )

      for track in tracks:
          print(f"{track.rank}. {track.artist} - {track.title}")


  asyncio.run(main())
  ```
</details>

## 📊 What the chart methods return

Shazam publishes its charts as CSV with three columns, so a chart entry is a
`ChartTrack` carrying a rank, an artist and a title, and nothing else. A chart
has no ids, no artwork and no provider links, so a chart entry cannot be passed
to `Serialize`. Nothing in the library resolves a chart row to a track id
either: Shazam retired the search endpoints that used to do it.

`limit` defaults to the whole chart, and `offset` skips entries from the top:
both are applied to the chart the service returns, which is always the full
one.

## 🔧 What data serialization gives you

`Serialize.full_track` turns the output of `recognize` into a `ResponseTrack`,
and `Serialize.track` turns the output of `track_about` into a `TrackInfo`.
Both carry the title, the artist, the artwork and the provider links, so you
no longer have to pick the fields out of the raw dictionary by hand.

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

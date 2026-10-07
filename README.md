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
  🎵 Is a FREE asynchronous library from reverse engineered Shazam API written in Python 3.10+ with asyncio and aiohttp. Recognizes a song from a file or from bytes, reads a track, and returns every chart Shazam publishes.

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
sample below ships with the repository, in `examples/data/`. The signature
covers 12 s of the audio, the window Shazam clients send;
`segment_duration_seconds` still takes another one and warns, and from 15 s up
Shazam finds nothing at all<br>

  ```python3
  import asyncio
  from shazamio import Serialize, Shazam


  async def main():
      async with Shazam() as shazam:
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
      async with Shazam() as shazam:
          about_track = await shazam.track_about(track_id=552406075)

          print(about_track)  # dict
          print(Serialize.track(data=about_track))  # pydantic model


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🍎🔑 Apple Music ids to Shazam track keys</i>
</summary>

Resolve Apple Music track ids to the Shazam track keys `track_about` takes, in
one request. A call with several ids keys every entry by the id Shazam stores,
which can be one you never sent, so read the values instead of indexing by what
you asked for. A call with a single id keys it by that id. Either way an id
Shazam has no track for is absent, so the map can be shorter than the list you
passed.<br>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      async with Shazam() as shazam:
          keys = await shazam.track_keys_from_apple_ids([1125281672, 1440650711])

          print(keys)  # {'1125281672': '325127876', '6781023657': '56670613'}


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔎🎶 Search tracks by text, through Apple's index</i>
</summary>

Shazam no longer answers text search, so this searches Apple's iTunes index and
fetches the Shazam track of every song found. Relevance and order are Apple's.
Songs Shazam has no track for are left out and versions sharing one Shazam track
come back once, so you can get fewer tracks than `limit`. Each song costs two
requests, which is why `limit` defaults to 5.<br>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      async with Shazam() as shazam:
          tracks = await shazam.search_tracks_via_itunes("daft punk one more time")

          print([track["title"] for track in tracks])
          # ['One More Time', 'One More Time (12 Mix)', "One More Time (Romanthony's Unplugged)"]


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
      async with Shazam() as shazam:
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
      async with Shazam() as shazam:
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
      async with Shazam() as shazam:
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
      async with Shazam() as shazam:
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
      async with Shazam() as shazam:
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

## 🔌 Closing what you open

A `Shazam` opens one connection pool on its first request and reuses it for
every later one, so ten calls no longer cost ten connections. The pool lives
until you close it, which `async with` does for you:

  ```python3
  async with Shazam() as shazam:
      ...
  ```

Without a close the pool stays open and `aiohttp` reports it when the object is
collected: `Unclosed client session`. `await shazam.close()` does the same job
where a block does not fit, and a request after either one raises
`RuntimeError: Session is closed`.

A pool belongs to the event loop it was opened on. A `Shazam` kept across
several `asyncio.run` calls opens a new pool on each new loop and abandons the
old one, which `aiohttp` reports the same way. A closed `Shazam` stays closed
in every loop. Prefer one `asyncio.run` around all the calls.

An `HTTPClient` you build yourself is yours to close: `Shazam` closes only the
client it builds for itself. `examples/recognize.py` shows both blocks.

## 🎯 When a match may be wrong

Shazam sometimes answers with a confident match for the wrong track, and some
recordings get one at every offset. `recognize(..., max_skew=1e-3)` turns an
answer whose first match is skewed beyond the limit into a no-match, which
removes most of those. It is off by default because it also rejects audio
played faster, slower or pitch-shifted; the `recognize` docstring has the
measurements.

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

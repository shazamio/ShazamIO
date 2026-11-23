<p align="center">
<a href="https://pypi.org/project/shazamio/"><img src="https://badge.fury.io/py/shazamio.svg" alt="PyPI version"></a>
<a href="https://pepy.tech/projects/shazamio"><img src="https://pepy.tech/badge/shazamio" alt="Downloads"></a>
<a href="https://pepy.tech/projects/shazamio"><img src="https://pepy.tech/badge/shazamio/month" alt="Downloads per month"></a>
<a href="https://github.com/shazamio/ShazamIO/blob/master/LICENSE.txt"><img src="https://img.shields.io/github/license/shazamio/ShazamIO.svg" alt="License"></a>
<br><br>

  <img width="1000" src="https://user-images.githubusercontent.com/64792903/109359596-ca561a00-7896-11eb-9c93-9cf1f283b1a5.png">
  🎵 Is a FREE asynchronous library from reverse engineered Shazam API written in Python 3.11+ with asyncio and aiohttp. Recognizes a song from a file or from bytes, reads a track, and returns every chart Shazam publishes.

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
covers 12 s of the audio, the window Shazam clients send.
`options=SearchParams(segment_duration_seconds=...)` takes another one and
warns, and from 15 s up Shazam finds nothing at all<br>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      async with Shazam() as shazam:
          out = await shazam.recognize("Gloria.ogg")

          print(out.track.title)  # I Will Survive


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
  from shazamio import Shazam


  async def main():
      async with Shazam() as shazam:
          track = await shazam.track_about(552406075)

          print(track.title, track.subtitle)


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🎵📺 YouTube video of a track</i>
</summary>

The video Shazam shows for a track, looked up by its artist and title<br>

  ```python3
  import asyncio
  from shazamio import Shazam


  async def main():
      async with Shazam() as shazam:
          out = await shazam.recognize("Gloria.ogg")

          video = await shazam.get_youtube_data(out.track.youtube_link)
          print(video.uri)  # https://youtu.be/6dYWe1c3OyU?autoplay=1


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

          print([track.title for track in tracks])
          # ['One More Time', 'One More Time (12 Mix)', "One More Time (Romanthony's Unplugged)"]


  asyncio.run(main())
  ```
</details>

<details>
<summary>
<i>🔝🎶🌏 Top tracks: world, country, city, genre</i>
</summary>

One method reads every chart Shazam publishes. With no argument it is the 200
most shazamed tracks worldwide; a country code, a city or a genre narrows it.
The city name is the one `services/charts/locations` publishes. Shazam offers
only a handful of genres per country, and asking for one it does not offer
raises `BadResponse` with status `404`<br>
<a href="https://www.shazam.com/charts/top-200/world">https://www.shazam.com/charts/top-200/world</a>

  ```python3
  import asyncio
  from shazamio import GenreMusic, Shazam


  async def main():
      async with Shazam() as shazam:
          world = await shazam.top_tracks()
          dutch = await shazam.top_tracks("NL")
          moscow = await shazam.top_tracks("RU", city="Moscow")
          rock = await shazam.top_tracks(genre=GenreMusic.ROCK)
          spanish_rap = await shazam.top_tracks("ES", genre=GenreMusic.HIP_HOP_RAP)

          for track in world[:10]:
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
`RuntimeError: Shazam is closed`.

A pool belongs to the event loop it was opened on. A `Shazam` kept across
several `asyncio.run` calls opens a new pool on each new loop and abandons the
old one, which `aiohttp` reports the same way. A closed `Shazam` stays closed
in every loop. Prefer one `asyncio.run` around all the calls.

## 🧦 Proxies, SOCKS and your own session

Every request goes through a transport, `AiohttpTransport()` unless you pass
one. Give it your own `aiohttp.ClientSession` to route traffic your way; the
transport never closes a session it was given:

  ```python3
  from aiohttp import ClientSession

  from shazamio import AiohttpTransport, Shazam

  async with (
      ClientSession(proxy="http://proxy.example.com:8080") as session,
      Shazam(transport=AiohttpTransport(session=session)) as shazam,
  ):
      out = await shazam.recognize("Gloria.ogg")
  ```

For SOCKS, build the session on a connector from `aiohttp-socks`:
`ClientSession(connector=ProxyConnector.from_url("socks5://127.0.0.1:1080"))`.
A session's `raise_for_status` is ignored, so every status still reaches the
retries and the errors below.

Another HTTP library plugs in as a subclass of `Transport` with two methods:
`send(request)`, which sends a `Request` once and returns a `Response` whatever
its status, or raises `TransportError` when no answer came, and `close()`.
`Shazam` does the rest, middleware, status checks and parsing included. A
transport you pass stays yours to close, so one can serve several `Shazam`
clients in turn.

## 🔁 Retries and middleware

Every request passes through the client's middleware on its way to the
transport, `[Retry()]` unless you pass your own list. `Retry` sends a request
answered `429` or any `5xx` again, by default until it has gone out 20 times,
with an exponential backoff from 0.2 s capped at 60 s. A `Retry-After` given in
seconds replaces the backoff, under the same cap. Here three attempts on a
`429` alone, and on a request that got no answer:

  ```python3
  from shazamio import Retry, Shazam

  Shazam(
      middleware=[
          Retry(attempts=3, statuses=frozenset({429}), on_transport_error=True),
      ],
  )
  ```

Without `on_transport_error=True` a `TransportError` is raised at once.
`middleware=[]` sends every request once. Each retry is logged at debug level
on the `shazamio._retry` logger.

A middleware is an async callable taking the `Request` and `call_next`; it may
change the request, answer it itself, or read the response on its way back. The
first one in the list runs outermost:

  ```python3
  import time

  from shazamio import CallNext, Request, Response, Retry, Shazam


  async def timed(request: Request, *, call_next: CallNext) -> Response:
      started = time.monotonic()
      response = await call_next(request)
      print(request.url, response.status, time.monotonic() - started)

      return response


  Shazam(middleware=[timed, Retry()])
  ```

## 🧩 Endpoints

Every method runs an endpoint from `shazamio.endpoints`, and `await shazam(endpoint)`
runs any of them, yours included. An `Endpoint` builds its `Request` from the
client's `Settings` and parses the answer's text; `Shazam` sends it through the
middleware and checks for `200` and the endpoint's `content_type` in between:

  ```python3
  from dataclasses import dataclass

  from shazamio import Endpoint, Request, Settings, Shazam, TrackInfo
  from shazamio.endpoints import TrackAbout


  @dataclass(frozen=True, kw_only=True)
  class RawTrack(Endpoint[str]):
      track_id: int

      def request(self, settings: Settings) -> Request:
          return TrackAbout(track_id=self.track_id).request(settings)

      def parse(self, payload: str) -> str:
          return payload


  async with Shazam() as shazam:
      track: TrackInfo = await shazam(TrackAbout(track_id=549952578))
      raw: str = await shazam(RawTrack(track_id=549952578))
  ```

## 🧪 Testing code that calls Shazam

`shazamio.testing.MockTransport` sends nothing: a function of yours answers
every request, and the transport keeps each one in `requests`:

  ```python3
  from shazamio import Request, Response, Shazam
  from shazamio.testing import MockTransport


  def answer(request: Request) -> Response:
      return Response(
          status=429,
          content_type="text/html",
          text="",
      )


  shazam = Shazam(transport=MockTransport(answer), middleware=[])
  ```

The answers go through the same middleware and checks as the service's, so
this one raises `RateLimited`; `middleware=[]` skips the waits the default
retries would add.

## 🚨 Errors

Every error the library raises about a request is a `ShazamError`:

| Error | Raised when |
|---|---|
| `BadResponse` | the service answered with another status or content type than the API answer; `.url`, the URL the endpoint built, and `.status` say which |
| `RateLimited` | a `BadResponse` for a throttled request, status `429`, still there after the retries; back off |
| `BadPayload` | the answer arrived and fits no model |
| `NotFound` | a country, city or Apple id the service does not know; also a `LookupError` |
| `TransportError` | no answer came: a failed connection or proxy, a timeout; the transport's own error is its `__cause__` |

A wrong argument raises `ValueError` or `TypeError` before any request is sent,
and a request on a closed `Shazam` raises `RuntimeError`.
`recognize` raises `SignatureError` when it cannot read the audio, a missing
file included.

## 🎯 When a match may be wrong

Shazam sometimes answers with a confident match for the wrong track, and some
recordings get one at every offset. `recognize(..., max_skew=1e-3)` turns an
answer whose first match is skewed beyond the limit into a no-match, which
removes most of those. It is off by default because it also rejects audio
played faster, slower or pitch-shifted; the `recognize` docstring has the
measurements.

## 📊 What the chart method returns

Shazam publishes its charts as CSV with three columns, so a chart entry is a
`ChartTrack` carrying a rank, an artist and a title, and nothing else. A chart
has no ids, no artwork and no provider links, so it is not a `TrackInfo`.
Nothing in the library resolves a chart row to a track id either: Shazam
retired the search endpoints that used to do it.

A row without exactly three fields is skipped and logged as a warning on the
`shazamio._parsers` logger, so a chart can come back shorter than the one Shazam
serves. The service always returns the whole chart; slice the list for a part
of it (`tracks[10:20]`).

## 🔧 What the track methods return

`recognize` returns a `ResponseTrack`, `track_about` and
`search_tracks_via_itunes` return `TrackInfo` objects, and `get_youtube_data`
returns a `YoutubeData`. A track carries the title, the artist, the artwork and
the provider links. Top-level keys that no field reads, such as `genres` or
`isrc`, stay on the model: read them as attributes (`track.genres`) or from
`track.model_extra`. The `images`, `hub` and `artists` objects do not: the
model keeps only the values its fields read from them (`photo_url`,
`apple_music_url`, `ringtone`, `providers`, `artist_id`), so
`images.background` or `hub.explicit` is gone. An answer that does not fit the
model raises `BadPayload`.

A stored payload becomes the same model through pydantic:
`TrackInfo.model_validate(payload)`.

<details>
<summary>
<i>Open photo: what song information looks like</i>
</summary>
<img src="https://user-images.githubusercontent.com/64792903/109454465-57e76480-7a65-11eb-956c-1bcac41d7de5.png">

</details>

## 📱 Recognition request profiles

Recognition defaults to the iPhone route, as in 0.9.0. To diagnose differences
between client profiles, select a fixed route explicitly:

```python
from shazamio import Device, Shazam

async with Shazam(recognition_device=Device.ANDROID) as shazam:
    result = await shazam.recognize("audio.wav")
```

`recognition_device` accepts `Device.IPHONE` (the default), `Device.ANDROID`, or
`Device.WEB`. Plain strings (`"iphone"`, `"android"`, or `"web"`) also work at
runtime; use the enum for type checking. Invalid values raise `ValueError` when
constructing the client.

Only the recognition URL's device segment changes. All profiles retain the
existing `X-Shazam-Platform: IPHONE` and `X-Shazam-AppVersion: 14.1.0` headers,
with a randomly selected Android Dalvik user agent. Other endpoints retain their
existing routes and headers.

This option does not change fingerprints, retries, or rate limits, and does not
rotate profiles automatically. A 429 still means the caller must back off. Changing
profiles can change response fields: web responses may omit `hub.providers`, and
Android responses may contain `intent://` Apple Music links. Applications depending
on those fields should retain the default until they have checked compatibility.

## ⬆️ Upgrading from 0.9

0.10 rebuilds the package around one `Shazam` client and breaks the API:

| 0.9 | 0.10 |
|---|---|
| `top_world_tracks()`, `top_country_tracks(country_code)`, `top_city_tracks(country_code, city_name=...)`, `top_world_genre_tracks(genre)`, `top_country_genre_tracks(country_code, genre=...)` | `top_tracks()`, `top_tracks(country_code)`, `top_tracks(country_code, city=...)`, `top_tracks(genre=...)`, `top_tracks(country_code, genre=...)` |
| `limit=` and `offset=` on the chart methods | slice the list: `tracks[offset:offset + limit]` |
| methods returning `dict` | `ResponseTrack`, `TrackInfo`, `YoutubeData` models |
| `Serialize.track(payload)`, `Serialize.full_track(payload)`, `Serialize.youtube(payload)` | `TrackInfo.model_validate(payload)`, `ResponseTrack.model_validate(payload)`, `YoutubeData.model_validate(payload)` |
| `proxy=` on every method, positional in `recognize(data, proxy)` and `track_about(track_id, proxy)` | a session of yours: `ClientSession(proxy=...)` passed as `Shazam(transport=AiohttpTransport(session=...))`, closed by you |
| a subclass of `HTTPClientInterface`, for SOCKS or anything else | `AiohttpTransport(session=...)` on the connector you need, or a `Transport` subclass for another HTTP library |
| `Shazam(http_client=HTTPClient(retry_options=ExponentialRetry(...)))` | `Shazam(middleware=[Retry(...)])`, whose `start_delay` and `max_delay` are `start_timeout` and `max_timeout`; `statuses` is now the whole set retried, so `statuses=S` with the default `retry_all_server_errors=True` becomes `statuses=frozenset(S) \| set(range(500, 600))`; `exceptions=` becomes `on_transport_error=True`, which retries every `TransportError`; `evaluate_response_callback=` and the other retry classes become a middleware of yours |
| `Shazam(endpoint_country="GB")` | `Shazam(country="GB")`, every argument by keyword |
| `Shazam(segment_duration_seconds=n)` | `recognize(..., options=SearchParams(segment_duration_seconds=n))` |
| `recognize(data, proxy, options)`, `options` positional | `recognize(data, options=...)`, `options` and `max_skew` by keyword |
| `send_recognize_request_v2(sig)`, also `sig=...` | `recognize_signature(signature)`, the keyword is `signature=` |
| `shazamio.schemas.models`, `shazamio.schemas.charts` | `shazamio` or `shazamio.models` |
| `FailedDecodeJson` for an empty answer, such as the `204` of an unknown track key | `BadResponse`, its `.status` says which |
| `FailedDecodeJson` for a body that is no JSON, `BadParseData` | `BadPayload` |
| `BadResponseStatus`, `BadContentType` | `BadResponse` |
| `BadCityName`, `BadCountryName`, `BadAppleIds` for an id the service does not know | `NotFound` |
| `BadAppleIds` for an empty id list | `ValueError`, before any request |
| `ValueError` for `recognize` data that is neither a path nor bytes | `TypeError` |
| `GeoService`, `HTTPClient`, `Serialize`, `CountryCode` | gone |
| `shazamio.exceptions`, `shazamio.enums` and the other submodules | `shazamio` itself; `shazamio.models`, `shazamio.endpoints` and `shazamio.testing` are the only public submodules |
| the attributes `headers()`, `language`, `endpoint_country`, `http_client`, `geo_service`, `core_recognizer` | gone, the constructor arguments are not exposed |
| a debug record per attempt on the `shazamio.request` logger | a debug record per retry on the `shazamio._retry` logger |
| Python 3.10, `aiohttp>=3.8.0`, `aiohttp-retry>=2.3` | Python 3.11, `aiohttp>=3.11`, no `aiohttp-retry` |
| `GenreMusic` as a plain `Enum` | a `StrEnum`: `f"{GenreMusic.ROCK}"` is `rock` |

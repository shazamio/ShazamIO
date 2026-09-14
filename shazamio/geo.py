from typing import Any

from shazamio.exceptions import BadCityName, BadCountryName
from shazamio.interfaces.client import HTTPClientInterface
from shazamio.misc import Request, ShazamUrl
from shazamio.typehints import CountryCode


class GeoService:
    """Resolves the URL slugs the chart paths are keyed by."""

    def __init__(self, client: HTTPClientInterface, *, request: Request) -> None:
        self.client = client
        self.request = request

    async def country_url_name(
        self,
        country: CountryCode,
        *,
        proxy: str | None = None,
    ) -> str:
        """Return a country's chart slug. Example: `RU` gives `russia`."""
        for entry in await self._countries(proxy=proxy):
            if entry["id"] == country:
                return entry["urlName"]

        msg: str = f"Country not found, check the country code: {country}"
        raise BadCountryName(msg)

    async def city_url_name(
        self,
        country: CountryCode,
        *,
        city: str,
        proxy: str | None = None,
    ) -> str:
        """Return a city's chart slug. Example: `Moscow` gives `moscow`."""
        for entry in await self._countries(proxy=proxy):
            if entry["id"] != country:
                continue

            for city_entry in entry["cities"]:
                if city_entry["name"] == city:
                    return city_entry["urlName"]

        msg: str = f"City not found, check the city name: {city}"
        raise BadCityName(msg)

    # Without the Shazam headers the edge answers `www.shazam.com` with the website
    #  itself, and the JSON decoder raises `FailedDecodeJson` on 1.7MB of HTML.
    async def _countries(self, *, proxy: str | None) -> list[dict[str, Any]]:
        data = await self.client.request(
            "GET",
            ShazamUrl.LOCATIONS,
            headers=self.request.headers(),
            proxy=proxy,
        )

        return data["countries"]

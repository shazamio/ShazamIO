from typing import Any, Final

import pytest

from shazamio import BadCityName, Shazam
from shazamio.typehints import CountryCode

# A city name shared by two countries, listed in the other country first, not
#  first among its own country's cities, and listed twice there, so only the
#  first match is the right one.
_COUNTRIES: Final[dict[str, Any]] = {
    "countries": [
        {"id": "BY", "cities": [{"name": "Moscow", "urlName": "moscow-by"}]},
        {
            "id": "RU",
            "cities": [
                {"name": "Kazan", "urlName": "kazan"},
                {"name": "Moscow", "urlName": "moscow"},
                {"name": "Moscow", "urlName": "moscow-oblast"},
            ],
        },
    ],
}


@pytest.fixture
def shazam_with_countries(shazam: Shazam, monkeypatch: pytest.MonkeyPatch) -> Shazam:
    async def request(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return _COUNTRIES

    monkeypatch.setattr(shazam.http_client, "request", request)
    return shazam


@pytest.mark.asyncio
async def test_the_city_slug_comes_from_the_requested_country(
    shazam_with_countries: Shazam,
) -> None:
    url_name = await shazam_with_countries.geo_service.city_url_name(
        CountryCode("RU"),
        city="Moscow",
    )

    assert url_name == "moscow"


@pytest.mark.asyncio
async def test_an_unknown_city_is_rejected(shazam_with_countries: Shazam) -> None:
    with pytest.raises(BadCityName):
        await shazam_with_countries.geo_service.city_url_name(
            CountryCode("RU"),
            city="Minsk",
        )

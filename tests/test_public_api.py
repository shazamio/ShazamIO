import importlib.resources
from typing import Final

import shazamio

# What the package promises to keep working. Removing a name from here is a
#  breaking change for anyone importing it, so it takes two deliberate edits.
_EXPORTS: Final[tuple[str, ...]] = (
    "BadCityName",
    "BadCountryName",
    "BadRegionName",
    "FailedDecodeJson",
    "GenreMusic",
    "GeoService",
    "HTTPClient",
    "SearchParams",
    "Serialize",
    "Shazam",
)


def test_the_installed_package_carries_the_typing_marker() -> None:
    assert importlib.resources.files("shazamio").joinpath("py.typed").is_file()


def test_the_package_exports_exactly_the_documented_surface() -> None:
    assert shazamio.__all__ == _EXPORTS


def test_every_exported_name_resolves() -> None:
    unresolvable = [name for name in shazamio.__all__ if not hasattr(shazamio, name)]

    assert unresolvable == []

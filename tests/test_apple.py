from typing import Final

import pytest

from shazamio import Shazam
from shazamio.apple import parse_apple_to_shazam_keys
from shazamio.exceptions import BadAppleIds, BadParseData

_GOOD_APPLE_ID: Final[int] = 1125281672
# The same recording as `1440650711`, under the id Shazam stores rather than the
#  one a caller asks for.
_CANONICALIZED_APPLE_ID: Final[int] = 1440650711


def test_a_mapping_is_read_as_served() -> None:
    assert parse_apple_to_shazam_keys('{"1125281672":"325127876"}') == {
        "1125281672": "325127876",
    }


def test_an_error_body_is_reported_as_bad_ids() -> None:
    with pytest.raises(BadAppleIds, match="Could not fetch ids"):
        parse_apple_to_shazam_keys('{"error":{"msg":"Could not fetch ids"}}')


def test_a_body_that_is_not_json_is_rejected() -> None:
    with pytest.raises(BadParseData):
        parse_apple_to_shazam_keys("<!doctype html>\n")


def test_a_body_that_is_json_but_not_a_mapping_is_rejected() -> None:
    with pytest.raises(BadParseData):
        parse_apple_to_shazam_keys('["325127876"]')


@pytest.mark.asyncio
async def test_no_ids_is_refused_before_anything_is_requested() -> None:
    with pytest.raises(BadAppleIds):
        await Shazam().track_keys_from_apple_ids([])


# Also pins the path-segment order: with `language` first and `country` second
#  the service answers `200 {"error":{"msg":"Could not fetch ids"}}`, so this
#  test fails as `BadAppleIds` if the two are ever swapped.
@pytest.mark.asyncio
async def test_an_apple_id_resolves_to_a_shazam_track_key() -> None:
    keys = await Shazam().track_keys_from_apple_ids([_GOOD_APPLE_ID])

    assert list(keys) == [str(_GOOD_APPLE_ID)]
    assert keys[str(_GOOD_APPLE_ID)].isdigit()


@pytest.mark.asyncio
async def test_the_map_is_keyed_by_the_ids_shazam_stores() -> None:
    keys = await Shazam().track_keys_from_apple_ids([_GOOD_APPLE_ID, _CANONICALIZED_APPLE_ID])

    assert len(keys) == 2
    assert str(_CANONICALIZED_APPLE_ID) not in keys


# Each of these resolves on its own to `56670613`, keyed by itself; together they
#  answer one entry, keyed by `6781023657`, which is neither of them.
@pytest.mark.asyncio
async def test_ids_sharing_one_track_collapse_into_a_single_entry() -> None:
    keys = await Shazam().track_keys_from_apple_ids([6781027645, 6781024437])

    assert len(keys) == 1
    assert "6781027645" not in keys
    assert "6781024437" not in keys


@pytest.mark.asyncio
async def test_an_id_the_service_cannot_resolve_at_all_is_reported() -> None:
    with pytest.raises(BadAppleIds, match="Could not fetch ids"):
        await Shazam().track_keys_from_apple_ids([0])

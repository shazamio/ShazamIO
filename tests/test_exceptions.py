import pickle

import pytest

from shazamio import BadPayload, BadResponse, NotFound, RateLimited, ShazamError


@pytest.mark.parametrize(
    ("error", "base"),
    [
        pytest.param(BadResponse, ShazamError, id="bad-response"),
        pytest.param(RateLimited, BadResponse, id="rate-limited"),
        pytest.param(BadPayload, ShazamError, id="bad-payload"),
        pytest.param(NotFound, ShazamError, id="not-found"),
        pytest.param(NotFound, LookupError, id="not-found-lookup"),
    ],
)
def test_every_error_is_caught_by_its_documented_base(
    *,
    error: type[ShazamError],
    base: type[Exception],
) -> None:
    assert issubclass(error, base)


# A raise inside a `ProcessPoolExecutor` worker reaches the parent through
#  `pickle`, so the rebuilt error has to keep its class, message and fields.
@pytest.mark.parametrize(
    "error",
    [pytest.param(BadResponse, id="bad-response"), pytest.param(RateLimited, id="rate-limited")],
)
def test_a_bad_response_survives_a_pickle_round_trip(*, error: type[BadResponse]) -> None:
    raised = error(
        "https://example.com answered 429",
        url="https://example.com",
        status=429,
    )
    raised.add_note("attempt 20 of 20")

    # The bytes are the ones dumped on the line itself, never untrusted input.
    rebuilt = pickle.loads(pickle.dumps(raised))  # noqa: S301

    assert (type(rebuilt), str(rebuilt), rebuilt.url, rebuilt.status, rebuilt.__notes__) == (
        error,
        "https://example.com answered 429",
        "https://example.com",
        429,
        ["attempt 20 of 20"],
    )
